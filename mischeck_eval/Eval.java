
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Random;
import java.util.SortedMap;
import java.util.TreeMap;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;

import data.History;
import data.Nurse;
import data.Scenario;
import data.Week;

/** Provides the basic search framework and the data structures required by the solving heuristics */
public class Eval {

	private static boolean PRINT_DEBUG = false;

	private static int TIMEOUT = 100000; //milliseconds
	private static int MAX_RESTARTS = 30;
	private static int MAX_STEPS_WITHOUT_IMPROVEMENT = 1000;
	private static String initName = "RandomMaxOptimum";
	private static String h1Name = "TabuSearch";
	private static String h2Name = "RandomWalk";
	private static double probH2 = 0.2;

	/** shiftAssignment[nurse][day] contains the id of the assigned shift (or -1 for a free day) */
	private int[][] shiftAssignment;
	/** skillsAssignment[nurse][day] holds the id of the skill the nurse is performing (ignored on free days) */
	private int[][] skillAssignment;

	// best solution found so far
	public int bestFitness = Integer.MAX_VALUE;
	public int lastImprovement = 0;
	private int[][] bestSolutionShifts;
	private int[][] bestSolutionSkills;

	private int nrRestarts = 0;
	private List<Integer> totalMoves = new ArrayList<>();
	private List<Integer> firstFeasible = new ArrayList<>();

	/** random generator, set seed for repeatability */
	public Random r = new Random(1234); //1234

	private Scenario sc;
	private Week w;
	private History h;
	public Evaluator eval;

	public Eval(Scenario sc, Week w, History h) {
		this.sc = sc;
		this.w = w;
		this.h = h;
		eval = new Evaluator(sc, h, w);
	}



	public int calculateFitnessFull(boolean setConflicts, boolean useArtificialPenalties) {
		return eval.calculateFitnessFull(shiftAssignment, skillAssignment, setConflicts, useArtificialPenalties);
	}



	private History buildHistory() {
		History h = new History();
		h.initAll(sc.nurses.length);

		int[][] schedule = bestSolutionShifts;

		for(int nurse = 0; nurse < sc.nurses.length; nurse++){
			//totalAssignments
			int nrAssign = this.h.totalAssignments[nurse];
			for(int d = 0; d < 7; d++){
				if(schedule[nurse][d] != -1) nrAssign++;
			}
			h.totalAssignments[nurse] = nrAssign;

			//weekends
			h.nrWorkingWeekends[nurse] = this.h.nrWorkingWeekends[nurse] + (schedule[nurse][5] != -1 || schedule[nurse][6] != -1 ? 1 : 0);

			//lastShift and consecutive work
			h.lastShift[nurse] = schedule[nurse][6];
			if(schedule[nurse][6] == -1){
				h.consecutiveFree[nurse] = 1;
				int d = 5;
				while(d >= 0 && schedule[nurse][d] == -1){
					h.consecutiveFree[nurse]++;
					d--;
				}
				h.consecutiveShift[nurse] = 0;
				h.consecutiveWork[nurse] = 0;
			} else {
				h.consecutiveWork[nurse] = 1;
				h.consecutiveShift[nurse] = 1;
				int d = 5;
				boolean shiftBlock = true;
				while(d >= 0 && schedule[nurse][d] != -1 ){
					h.consecutiveWork[nurse]++;
					if(shiftBlock && schedule[nurse][d] == h.lastShift[nurse]){
						h.consecutiveShift[nurse]++;
					} else shiftBlock = false;
					d--;
				}
				h.consecutiveFree[nurse] = 0;

			}
		}

		return h;
	}
	public String assignmentString(int shift, int skill){
		if(shift == -1) return "Free";

		return sc.shifts[shift]+"@"+sc.skills[skill];
	}

	public String formatSolution(int[][] shifts, int[][] skills) {

		String s = String.format("\t\tMo \t\tTue \t\tWe \t\tTh \t\tFr \t\tSa \t\tSu \n");

		for(int i = 0; i < sc.nurseIDs.length; i++){
			s += String.format("%-14s: ", sc.nurseIDs[i]);
			for(int d=0; d < 7; d++){
				if(shifts[i][d] < 0)
					s += String.format("%-16s", "Free");
				else
					s += String.format("%-16s", sc.shifts[shifts[i][d]] + "@" + sc.skills[skills[i][d]]);
			}
			s += "\n";
		}

		return s;
	}

	public void printDebug(Object out) {
		if(PRINT_DEBUG){
			System.out.println(out.toString());
		}
	}

	/**
	 * @param args
	 */
	public static void main(String[] args) {

		// Parse command line options
		CommandLine cl = parseArgs(args);

		String instanceName = cl.getOptionValue("scenario");
		int nrWeeks = Integer.parseInt(instanceName.substring(5));

		// ==1 lol
		String[] weekIDs = cl.getOptionValues("weeks");
		//System.out.println(weekIDs[1]);
		//String[] weekIDs = 1;SolutionPar

		int historyID = Integer.parseInt(cl.getOptionValue("h"));

		String customfp = cl.getOptionValue("csol", "");
		System.out.println("custom sol: " + customfp);


		System.out.println("INSTANCE "+instanceName+" W "+Arrays.toString(weekIDs)+" H"+historyID);

		// Read instance

		Scenario sc = new ScenarioParser(instanceName).parse();


		//Week[] weeks = new Week[nrWeeks];
		Week[] weeks = new Week[1];
		for(int i=0; i < weeks.length; i++){
			weeks[i] = new WeekParser(instanceName, weekIDs[i], sc).parse();
			weeks[i].index = i;
		}
		History h = new HistoryParser(instanceName, historyID, sc).parse();

		int totalFitness = 0;

        

		if(cl.hasOption("sol")){

			//Parse solution files
			int i = 0;
			System.out.println(i);

			String weeksString = Arrays.toString(cl.getOptionValues("w")).replace("[", "").replace("]", "").replace(", ", "-");

			//Trying to grab json files
			//String solutionFile = instanceName+"/Solution_H_"+historyID+"-WD_"+weeksString+"/"+"Sol-"+instanceName+"-"+weekIDs[i]+"-"+i+".json";

			String solutionFile = customfp;

			SolutionParser sp = new SolutionParser(solutionFile, sc);
			sp.parse();

			Eval s = new Eval(sc, weeks[i], h);
			s.shiftAssignment = sp.shiftAssignment;
			s.skillAssignment = sp.skillAssignment;

			if(!cl.hasOption("summary")){
				System.out.println("WEEK "+(i+1)+"(ID: "+weekIDs[i]+")");
				System.out.println(s.formatSolution(s.shiftAssignment, s.skillAssignment));
			}

			s.eval.PRINT_CONFLICTS = cl.hasOption("printConflicts");
			int fitness = s.calculateFitnessFull(false, false);
			s.eval.PRINT_CONFLICTS = true;
			totalFitness += fitness;

			System.out.println("Penalty for week "+(i+1)+": "+fitness);

			s.bestSolutionShifts = s.shiftAssignment;
			s.bestSolutionSkills = s.skillAssignment;
			h = s.buildHistory();

			//can rmv
			System.out.println("Total Fitness: "+totalFitness);

		} else {
            System.out.println("NOT GENERATING NEW");
		}
		System.out.println("-------------------------------------");
	}

	private static CommandLine parseArgs(String[] args){
		CommandLineParser parser = new DefaultParser();

		Options opt = new Options();

		opt.addOption(Option.builder("s").longOpt("scenario").hasArg().argName("SCENARIO").required()
				.desc("The name of the scenario to use").build());

		opt.addOption(Option.builder("w").longOpt("weeks").hasArgs().argName("WEEKS").required()
				.valueSeparator(',')
				.desc("A comma-separated list of week indices").build());

		opt.addOption(Option.builder("h").longOpt("history").hasArg().argName("HISTORY").required()
				.desc("The index of the history file").build());

		opt.addOption(Option.builder("sol").longOpt("solution").desc("Parse only the provided solution for this instance").build());
		opt.addOption(Option.builder("e").longOpt("export").desc("Prints the solution to an output file").build());

		//termination criteria
		opt.addOption(Option.builder("t").longOpt("timeout").hasArg().type(Number.class).desc("Maximum time for a single stage (including restarts, in ms)").build());
		opt.addOption(Option.builder("r").longOpt("restarts").hasArg().type(Number.class).desc("Maximum number of restarts").build());
		opt.addOption(Option.builder("m").longOpt("moves").hasArg().type(Number.class).desc("Maximum number of moves without improvement before a restart").build());

		//Output options
		opt.addOption(Option.builder("d").longOpt("debug").desc("Print additional debug information").build());
		opt.addOption(Option.builder().longOpt("printConflicts").desc("Prints a list of conflicts for each solution").build());
		opt.addOption(Option.builder().longOpt("summary").desc("Prints only a short summary instead of the full solution").build());

		// Heuristic options
		opt.addOption(Option.builder("i").longOpt("init").hasArg().desc("Initialization method to use (default: RandomMaxOptimum)").build());
		opt.addOption(Option.builder("h1").longOpt("heuristic1").hasArg().desc("The name of the first heuristic (default: TabuSearch)").build());
		opt.addOption(Option.builder("h2").longOpt("heuristic2").hasArg().desc("The name of the second heuristic (default: RandomWalk)").build());
		opt.addOption(Option.builder("p2").longOpt("prob-heuristic2").hasArg().type(Number.class).desc("Probability that heuristic 2 is chosen (default: 0.2)").build());

		//Use custom sol file
		opt.addOption(Option.builder().longOpt("csol").hasArg().desc("custom sol fp").build());

		try {
			CommandLine cl = parser.parse(opt, args);

			//some validity checks
			if(!cl.getOptionValue("s").matches("n[0-9]{3}w[48]")){
				throw new IllegalArgumentException("Unknown scenario (required format: n[0-9]{3}w[48])");
			}
			int nrWeeks = Integer.parseInt(cl.getOptionValue("s").substring(5));
			if(nrWeeks != cl.getOptionValues("w").length){
				throw new IllegalArgumentException("This instance has a planning horizon of "+nrWeeks+" weeks");				
			}
			if(!cl.getOptionValue("h").matches("[012]")){
				throw new IllegalArgumentException("The history id must be between 0 and 2");				
			}

			//set parameters if given
			if(cl.hasOption("t")){
				TIMEOUT = ((Number)cl.getParsedOptionValue("t")).intValue();
			}
			if(cl.hasOption("r")){
				MAX_RESTARTS = ((Number)cl.getParsedOptionValue("r")).intValue();
			}
			if(cl.hasOption("m")){
				MAX_STEPS_WITHOUT_IMPROVEMENT = ((Number)cl.getParsedOptionValue("m")).intValue();				
			}
			if(cl.hasOption("i")){
				initName = cl.getOptionValue("i");				
			}
			if(cl.hasOption("h1")){
				h1Name = cl.getOptionValue("h1");				
			}
			if(cl.hasOption("h2")){
				h2Name = cl.getOptionValue("h2");				
			}
			if(cl.hasOption("p2")){
				probH2 = ((Number)cl.getParsedOptionValue("p2")).doubleValue();				
			}
			if(cl.hasOption("d")){
				PRINT_DEBUG = true;				
			}

			return cl;

		} catch (ParseException | IllegalArgumentException e ) {
			new HelpFormatter().printHelp("Solver", e.getMessage(), opt, null, true);
			System.exit(1);
			return null; //dummy return
		}
	}
}
