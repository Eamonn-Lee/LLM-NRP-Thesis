import java.util.ArrayList;
import java.util.List;

import data.Contract;
import data.History;
import data.Scenario;
import data.Week;

/** Provides a method to evaluate the fitness function of a given schedule */
public class Evaluator {

	public static final int P_UNDERSTAFFING_MIN = 3000;
	public static final int P_UNDERSTAFFING_OPT = 30;
	public static final int P_FORBIDDEN_SEQUENCE = 1000;
	public static final int P_CONSECUTIVE_ASSIGNMENTS = 30;
	public static final int P_CONSECUTIVE_DAYS_OFF = 30;
	public static final int P_CONSECUTIVE_SHIFTS = 15;
	public static final int P_SHIFT_OFF_REQUEST = 10;
	public static final int P_COMPLETE_WEEKEND = 30;
	public static final int P_TOTAL_ASSIGNMENTS = 20;
	public static final int P_TOTAL_WEEKENDS = 30;
	public static final int P_AVERAGE_ASSIGNMENTS = 30;
	public static final int P_NEXT_WEEK_RESTRICTION = 10;

	private Scenario sc;
	private History h;
	private Week w;

	/** true if the last (fully) evaluated solution fulfills all hard constraints */
	public boolean isFeasible;
	/** true if the last (fully) evaluated solution fulfills all minimum cover requirements */
	public boolean minStaffing;
	public boolean PRINT_CONFLICTS = false;
	/** If true, the solver will keep a list of cells appearing in a conflict in the current solution */
	public boolean listConflicts;
	public List<Integer> cellsInConflict = new ArrayList<Integer>();

	/** Caches the results of the last evaluation to speed up later runs */
	private int[] dayCache;
	private int[] nurseCache;
	/** staffingCache[day][shift][skill] */
	private int[][][] staffingCache;

	private int[][] shiftAssignment;
	private int[][] skillAssignment;

	//	public long timeDay;
	//	public long timeNurse;
	//	public long timePrefs;
	//	public long timeFull;
	//	public long timeUpdate;
	//	
	//	public int callsDay;
	//	public int callsNurse;
	//	public int callsPrefs;
	//	public int callsFull;
	//	public int callsUpdate;


	public Evaluator(Scenario sc, History h, Week w) {

		this.sc = sc;
		this.h = h;
		this.w = w;

		dayCache = new int[7];
		nurseCache = new int[sc.nurses.length];
		staffingCache = new int[7][sc.shifts.length][sc.skills.length];
	}

	/** 
	 * Calculates the fitness function of the given schedule
	 * @param setConflicts 
	 * @param useArtificialPenalties
	 */
	public int calculateFitnessFull(int[][] shiftAssignment, int[][] skillAssignment, boolean setConflicts, boolean useArtificialPenalties){

		//long start = System.nanoTime();

		if(!listConflicts) setConflicts = false;

		this.shiftAssignment = shiftAssignment;
		this.skillAssignment = skillAssignment;

		int fitness = 0;
		boolean[][] conflictMatrix = new boolean[sc.nurseIDs.length][7];

		isFeasible = true;

		//Understaffing (minimum and optimum)
		int[][][] staffing = new int[7][sc.shifts.length][sc.skills.length];
		for(int i = 0; i < sc.nurses.length; i++){
			for(int d = 0; d < 7; d++){
				int shift = shiftAssignment[i][d];
				if(shift != -1){
					int skill = skillAssignment[i][d];
					staffing[d][shift][skill]++;
				}
			}
		}
		staffingCache = staffing;

		for(int day = 0; day < 7; day++){
			int dayFitness = evaluateDay(day, staffing[day], setConflicts, conflictMatrix, useArtificialPenalties);
			fitness += dayFitness;
			dayCache[day] = dayFitness;
		}

		for(int nurse = 0; nurse < sc.nurses.length; nurse++){
			int nurseFitness = evaluateNurse(nurse, setConflicts, conflictMatrix, useArtificialPenalties);
			fitness += nurseFitness;
			nurseCache[nurse] = nurseFitness;
		}


		//Preferences (shift-off requests)
		fitness += evaluateRequests(setConflicts, conflictMatrix);



		//generate list of conflicted cells
		if(setConflicts){
			cellsInConflict.clear();
			for(int i = 0; i < sc.nurses.length; i++){
				for(int d = 0; d < 7; d++){
					if(conflictMatrix[i][d]){
						cellsInConflict.add(i*7+d);
					}
				}
			}
		}

		//timeFull += System.nanoTime() - start;
		//callsFull++;

		return fitness;

	}

	/** Uses a cache of fitness values calculated for the current solution (last call of {@link Evaluator#calculateFitnessFull}).
	 * Only fitness values of changed days and nurses are recalculated.
	 * Should be used by heuristics during the exploration of the local neighbourhood, after a small change to the current solution */
	public int evaluateFitnessUpdate(int[][] shiftAssignment, int[][] skillAssignment, boolean[] changedDays, boolean[] changedNurses){

		//long start = System.nanoTime();

		this.shiftAssignment = shiftAssignment;
		this.skillAssignment = skillAssignment;

		int fitness = 0;

		isFeasible = true;

		//Understaffing (minimum and optimum)
		int[][][] staffing = new int[7][sc.shifts.length][sc.skills.length];
		for(int d = 0; d < 7; d++){
			if(!changedDays[d]){
				staffing[d] = staffingCache[d];
			} else {
				for(int i = 0; i < sc.nurses.length; i++){
					int shift = shiftAssignment[i][d];
					if(shift != -1){
						int skill = skillAssignment[i][d];
						staffing[d][shift][skill]++;
					}
				}
			}
		}

		for(int day = 0; day < 7; day++){
			int dayFitness = changedDays[day] ? evaluateDay(day, staffing[day], false, null, true) : dayCache[day];
			fitness += dayFitness;
		}

		for(int nurse = 0; nurse < sc.nurses.length; nurse++){
			int nurseFitness = changedNurses[nurse] ? evaluateNurse(nurse, false, null, true) : nurseCache[nurse];
			fitness += nurseFitness;
		}

		//Preferences (shift-off requests)
		fitness += evaluateRequests(false, null);

		//timeUpdate += System.nanoTime() - start;
		//callsUpdate++;

		return fitness;
	}

	private int evaluateDay(int day, int[][] staffing, boolean setConflicts, boolean[][] conflictMatrix, boolean useArtificialPenalties) {
		//long start = System.nanoTime();

		int fitness = 0;
		for(int sh = 0; sh < sc.shifts.length; sh++){
			for(int sk = 0; sk < sc.skills.length; sk++){
				int min = w.minRequirements[day][sh][sk];
				int opt = w.optRequirements[day][sh][sk];
				if(staffing[sh][sk] < min){
					if(useArtificialPenalties){
						fitness += (min - staffing[sh][sk]) * P_UNDERSTAFFING_MIN;

						isFeasible = false;
						minStaffing = false;

						if(PRINT_CONFLICTS) System.out.println("MINIMUM STAFFING @ "+day+":"+sh+":"+sk+" - "+fitness);

						if(setConflicts){
							for(int i = 0; i < sc.nurseIDs.length; i++){
								conflictMatrix[i][day] = (shiftAssignment[i][day] != sh || skillAssignment[i][day] != sk);
							}
						}
					}
				} else if(staffing[sh][sk] < opt){
					fitness += (opt - staffing[sh][sk]) * P_UNDERSTAFFING_OPT;

					if(PRINT_CONFLICTS) System.out.println("OPTIMUM STAFFING @ "+day+":"+sh+":"+sk+" - "+fitness);

					if(setConflicts){
						for(int i = 0; i < sc.nurseIDs.length; i++){
							conflictMatrix[i][day] = (shiftAssignment[i][day] != sh || skillAssignment[i][day] != sk);
						}
					}
				}
			}
		}

		//timeDay += System.nanoTime()-start;
		//callsDay++;
		return fitness;
	}

	private int evaluateNurse(int nurse, boolean setConflicts, boolean[][] conflictMatrix, boolean useArtificialPenalties){
		//long start = System.nanoTime();

		int fitness = 0;

		Contract contract = sc.nurses[nurse].contract;

		//forbidden sequences
		if(useArtificialPenalties){
			int prvShift = h.lastShift[nurse];
			for(int d = 0; d < 7; d++){
				int currShift = shiftAssignment[nurse][d];

				if(prvShift >= 0 && currShift >= 0 && sc.forbiddenSequence[prvShift][currShift]){
					fitness += P_FORBIDDEN_SEQUENCE;

					isFeasible = false;

					if(PRINT_CONFLICTS) System.out.println("FORBIDDEN SEQUENCE @ "+nurse+":"+d+" - "+fitness);

					if(setConflicts){
						conflictMatrix[nurse][d] = true;
						if(d > 0) conflictMatrix[nurse][d-1] = true;
					}
				}
				prvShift = currShift;
			}
		}

		//assignment sequence length
		int minConsWork = contract.minConsWork;
		int maxConsWork = contract.maxConsWork;
		int minConsFree = contract.minConsFree;
		int maxConsFree = contract.maxConsFree;

		int lastShift = h.lastShift[nurse];
		int consecBlock = (lastShift == -1) ? h.consecutiveFree[nurse] : h.consecutiveWork[nurse];
		int consecShift = h.consecutiveShift[nurse];

		for(int day = 0; day < 7; day++){
			//Case 1: both shift and work/free block continues, do nothing
			if(shiftAssignment[nurse][day] == lastShift){
				consecBlock++;
				consecShift++;
			}
			//Case 2: Free block ends: Check bounds
			else if(lastShift == -1){

				if(consecBlock < minConsFree || consecBlock > maxConsFree){
					int distance = Math.max(0, Math.max(minConsFree - consecBlock, consecBlock - maxConsFree));
					if(consecBlock > maxConsFree) distance = Math.min(day, distance); // adjust for already counted penalties in previous weeks
					fitness += P_CONSECUTIVE_DAYS_OFF * distance;

					if(PRINT_CONFLICTS) System.out.println("CONSECUTIVE FREE x"+distance+" @ "+nurse+":"+(day-consecBlock)+"-"+(day-1)+" - "+fitness);

					if(setConflicts){
						//all cells of the block and the two neighbours are marked as conflicts
						for(int i = 0; i < consecBlock + 2; i++){
							if(day-i >= 0) conflictMatrix[nurse][day-i] = true;
						}
					}
				}

				lastShift = shiftAssignment[nurse][day];
				consecBlock = 1;
				consecShift = 1;
				//Case 3: Any other block ends (either shift+work or only shift)
			} else {

				//Case 3a: shift ended, work block might continue
				if(consecShift < sc.consShifts[lastShift][0] || consecShift > sc.consShifts[lastShift][1]){
					int distance = Math.max(0, Math.max(sc.consShifts[lastShift][0] - consecShift, consecShift - sc.consShifts[lastShift][1]));
					if(consecShift > sc.consShifts[lastShift][1]) distance = Math.min(day, distance); // adjust for already counted penalties in previous weeks
					fitness += P_CONSECUTIVE_SHIFTS * distance;

					if(PRINT_CONFLICTS) System.out.println("CONSECUTIVE SHIFT x"+distance+" @ "+nurse+":"+(day-consecShift)+"-"+(day-1)+" - "+fitness);

					if(setConflicts){
						//all cells of the block and the two neighbours are marked as conflicts
						for(int i = 0; i < consecShift + 2; i++){
							if(day-i >= 0) conflictMatrix[nurse][day-i] = true;
						}
					}
				} 

				//Case 3b: Work block ended
				if(shiftAssignment[nurse][day] == -1){
					if(consecBlock < minConsWork || consecBlock > maxConsWork){
						int distance = Math.max(0, Math.max(minConsWork - consecBlock, consecBlock - maxConsWork));
						if(consecBlock > maxConsWork) distance = Math.min(day, distance); // adjust for already counted penalties in previous weeks
						fitness += P_CONSECUTIVE_ASSIGNMENTS * distance;

						if(PRINT_CONFLICTS) System.out.println("CONSECUTIVE WORK x"+distance+" @ "+nurse+":"+(day-consecBlock)+"-"+(day-1)+" - "+fitness);

						if(setConflicts){
							//all cells of the block and the two neighbours are marked as conflicts
							for(int i = 0; i < consecBlock + 2; i++){
								if(day-i >= 0) conflictMatrix[nurse][day-i] = true;
							}
						}
					}

					consecBlock = 1;
				} else {
					consecBlock++;
				}

				lastShift = shiftAssignment[nurse][day];
				consecShift = 1;
			}
		}

		//last day, check maxLength again! 
		if((lastShift == -1 && consecBlock > maxConsFree)
				|| (lastShift != -1 && consecBlock > maxConsWork)){

			int max = (lastShift == -1) ? maxConsFree : maxConsWork;
			int distance = consecBlock - max;
			distance = Math.min(7, distance); // adjust for already counted penalties in previous weeks
			fitness += distance * ((lastShift == -1) ? P_CONSECUTIVE_DAYS_OFF : P_CONSECUTIVE_ASSIGNMENTS);

			if(PRINT_CONFLICTS) System.out.println("CONSECUTIVE BLOCK x"+distance+" @ "+nurse+":"+(7-consecBlock)+"-"+6+" - "+fitness);

			if(setConflicts){
				//all cells of the block and the two neighbours are marked as conflicts
				for(int i = 0; i < consecBlock + 1; i++){
					if(6-i >= 0) conflictMatrix[nurse][6-i] = true;
				}
			}
		}
		if(lastShift != -1 && consecShift > sc.consShifts[lastShift][1]){
			int distance = consecShift - sc.consShifts[lastShift][1];
			distance = Math.min(7, distance); // adjust for already counted penalties in previous weeks
			fitness += distance * P_CONSECUTIVE_SHIFTS;

			if(PRINT_CONFLICTS) System.out.println("CONSECUTIVE SHIFT x"+distance+" @ "+nurse+":"+(7-consecShift)+"-"+6+" - "+fitness);

			if(setConflicts){
				//all cells of the block and the two neighbours are marked as conflicts
				for(int i = 0; i < consecShift + 1; i++){
					if(6-i >= 0) conflictMatrix[nurse][6-i] = true;
				}
			}
		}
		
		//calculate how much the assignment of the last block restricts the options for the following week
		if(useArtificialPenalties && w.index < sc.nrWeeks-1){
			if(lastShift == -1 && consecBlock < minConsFree){ // not enough free days -> forces free days
				fitness += P_NEXT_WEEK_RESTRICTION * sc.shifts.length * (minConsFree-consecBlock);
				
				if(PRINT_CONFLICTS) System.out.println("NEXT WEEK RESTRICTED @ "+nurse+": ENFORCES "+ (minConsFree - consecBlock) +"FREE DAYS - "+fitness);
				if(setConflicts){
					for(int i=6; 6-i < consecBlock+1 && i >= 0; i--) conflictMatrix[nurse][i] = true;
				}
			} else if(lastShift == -1 && consecBlock >= maxConsFree){ // max free days -> forbids free day
				fitness += P_NEXT_WEEK_RESTRICTION;
				
				if(PRINT_CONFLICTS) System.out.println("NEXT WEEK RESTRICTED @ "+nurse+": FORBIDS "+ 1 +"FREE DAY - "+fitness);
				if(setConflicts){
					for(int i=6; 6-i < consecBlock && i >= 0; i--) conflictMatrix[nurse][i] = true;
				}
			}
			
			if(lastShift != -1 && consecBlock < minConsWork){ // not enough work days -> forbids free days
				fitness += P_NEXT_WEEK_RESTRICTION * (minConsWork-consecBlock);
				
				if(PRINT_CONFLICTS) System.out.println("NEXT WEEK RESTRICTED @ "+nurse+": FORBIDS "+ (minConsWork - consecBlock) +"FREE DAYS - "+fitness);
				if(setConflicts){
					for(int i=6; 6-i < consecBlock+1 && i >= 0; i--) conflictMatrix[nurse][i] = true;
				}

			} else if(lastShift != -1 && consecShift < sc.consShifts[lastShift][0]){ // not enough of a single shift -> forces this shift
				fitness += P_NEXT_WEEK_RESTRICTION * sc.shifts.length * (sc.consShifts[lastShift][0] - consecShift);
				
				if(PRINT_CONFLICTS) System.out.println("NEXT WEEK RESTRICTED @ "+nurse+": ENFORCES "+ (sc.consShifts[lastShift][0] - consecShift) +" "+ sc.shifts[lastShift] +"- "+fitness);
				if(setConflicts){
					for(int i=6; 6-i < consecShift+1 && i >= 0; i--) conflictMatrix[nurse][i] = true;
				}
			}
			
			if(lastShift != -1 && consecBlock >= maxConsWork){ // too much work -> forces free day
				fitness += P_NEXT_WEEK_RESTRICTION * sc.shifts.length;
				
				if(PRINT_CONFLICTS) System.out.println("NEXT WEEK RESTRICTED @ "+nurse+": ENFORCES "+ 1 +"FREE DAY - "+fitness);
				if(setConflicts){
					for(int i=6; 6-i < consecBlock && i >= 0; i--) conflictMatrix[nurse][i] = true;
				}

			} else if(lastShift != -1 && consecShift >= sc.consShifts[lastShift][1]){ // too much of a single shift -> forbids this shift
				fitness += P_NEXT_WEEK_RESTRICTION;
				
				if(PRINT_CONFLICTS) System.out.println("NEXT WEEK RESTRICTED @ "+nurse+": FORBIDS "+ 1 +" "+ sc.shifts[lastShift] +" - "+fitness);
				if(setConflicts){
					for(int i=6; 6-i < consecShift && i >= 0; i--) conflictMatrix[nurse][i] = true;
				}
			}
		}

		//Complete weekends
		if(sc.nurses[nurse].contract.completeWeekend){
			if((shiftAssignment[nurse][5] == -1) != (shiftAssignment[nurse][6] == -1)){
				fitness += P_COMPLETE_WEEKEND;

				if(PRINT_CONFLICTS) System.out.println("COMPLETE WEEKEND @ "+nurse+":5-6"+" - "+fitness);

				if(setConflicts){
					conflictMatrix[nurse][5] = true;
					conflictMatrix[nurse][6] = true;

				}
			}
		}

		//Total Assignments (relevant only in later weeks)
		int minAssignment = contract.minAssignments;
		int maxAssignment = contract.maxAssignments;

		int assignments = h.totalAssignments[nurse];
		for(int d = 0; d < 7; d++){
			if(shiftAssignment[nurse][d] != -1) assignments++;
		}

		//max
		if(assignments > maxAssignment){
			int distance = assignments - maxAssignment;
			distance = Math.min(distance, assignments - h.totalAssignments[nurse]); //at most this week's assignments
			fitness += P_TOTAL_ASSIGNMENTS * distance;

			if(PRINT_CONFLICTS) System.out.println("TOTAL ASSIGNMENT MAX x"+distance+" @ "+nurse+"("+assignments+" of "+maxAssignment+")"+" - "+fitness);

			if(setConflicts){
				for(int d = 0; d < 7; d++){
					if(shiftAssignment[nurse][d] != -1) conflictMatrix[nurse][d] = true;
				}					
			}
		}

		//min
		int requiredAssignment = minAssignment - 7 * (sc.nrWeeks-1-w.index);
		if(assignments < requiredAssignment){
			int distance = requiredAssignment - assignments;
			distance = Math.min(distance, 7-(assignments - h.totalAssignments[nurse])); //at most this week's free days
			fitness += P_TOTAL_ASSIGNMENTS * distance;

			if(PRINT_CONFLICTS) System.out.println("TOTAL ASSIGNMENT MIN x"+distance+" @ "+nurse+"("+assignments+" of "+minAssignment+")"+" - "+fitness);

			if(setConflicts){
				for(int d = 0; d < 7; d++){
					if(shiftAssignment[nurse][d] == -1) conflictMatrix[nurse][d] = true;
				}
			}					
		}



		//Total weekends
		boolean thisWeekend = shiftAssignment[nurse][5] != -1 || shiftAssignment[nurse][6] != -1;

		int weekends = h.nrWorkingWeekends[nurse] + (thisWeekend ? 1 : 0);

		if(weekends > contract.maxWeekends && thisWeekend){
			fitness += P_TOTAL_WEEKENDS;

			if(PRINT_CONFLICTS) System.out.println("TOTAL WEEKENDS @ "+nurse+"("+weekends+" of "+contract.maxWeekends+")"+" - "+fitness);

			if(setConflicts){
				if(shiftAssignment[nurse][5] != -1) conflictMatrix[nurse][5] = true;
				if(shiftAssignment[nurse][6] != -1) conflictMatrix[nurse][6] = true;
			}

		}

		//Average assignments (assigns penalties to nurses scheduled above or below the expected average)
		// Favors schedules that have a balanced distribution over the weeks
		if(useArtificialPenalties && w.index < sc.nrWeeks-1){
			int minAvgAssignment = (int) Math.ceil(contract.minAssignments * (w.index+1) / (double) sc.nrWeeks);
			int maxAvgAssignment = (int) Math.floor (contract.maxAssignments * (w.index+1) / (double) sc.nrWeeks);

			//max
			if(assignments > maxAvgAssignment){
				int distance = assignments - maxAvgAssignment;
				fitness += P_AVERAGE_ASSIGNMENTS * distance;

				if(PRINT_CONFLICTS) System.out.println("AVERAGE ASSIGNMENT @ "+nurse+"("+minAvgAssignment+"-"+maxAvgAssignment+")"+" - "+fitness);

				if(setConflicts){
					for(int d = 0; d < 7; d++){
						if(shiftAssignment[nurse][d] != -1) conflictMatrix[nurse][d] = true;
					}
				}
			}

			//min
			if(assignments < minAvgAssignment){
				int distance = minAvgAssignment - assignments;
				fitness += P_TOTAL_ASSIGNMENTS * distance;

				if(PRINT_CONFLICTS) System.out.println("AVERAGE ASSIGNMENT @ "+nurse+"("+minAvgAssignment+"-"+maxAvgAssignment+")"+" - "+fitness);

				if(setConflicts){
					for(int d = 0; d < 7; d++){
						if(shiftAssignment[nurse][d] == -1) conflictMatrix[nurse][d] = true;
					}					
				}
			}
		}
		
		//timeNurse += System.nanoTime() - start;
		//callsNurse++;

		return fitness;
	}

	private int evaluateRequests(boolean setConflicts, boolean[][] conflictMatrix) {
		//long start = System.nanoTime();

		int fitness = 0;
		for(int i = 0; i < w.shiftOffRequested.length; i++){
			int nurse = w.shiftOffRequested[i][0];
			int day = w.shiftOffRequested[i][1];
			int shift = w.shiftOffRequested[i][2];

			if((shift == -1 && shiftAssignment[nurse][day] != -1) 
					|| (shift != -1 && shiftAssignment[nurse][day] == shift)){
				fitness += P_SHIFT_OFF_REQUEST;

				if(PRINT_CONFLICTS) System.out.println("SHIFT-OFF REQUEST @ "+nurse+":"+day+" - "+fitness);

				if(setConflicts){
					conflictMatrix[nurse][day] = true;
				}
			}
		}

		//timePrefs += System.nanoTime() - start;
		//callsPrefs++;

		return fitness;
	}


	/** returns true if the staffing for the given shift and skill combination is not more than the minimum cover required */
	public boolean isMinimumCover(int day, int shift, int skill){
		return (shift == -1) ? false : staffingCache[day][shift][skill] <= w.minRequirements[day][shift][skill];
	}
}
