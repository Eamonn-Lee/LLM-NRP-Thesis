package data;

import java.util.HashMap;
import java.util.Map;

public class Scenario {
	
	public int nrWeeks;
	public String[] skills;
	
	public Map<String, Contract> contracts = new HashMap<>();
	public Nurse[] nurses;
	public String[] nurseIDs;

	public String[] shifts;
	/** #shifts x 2, min and max number of consecutive shifts of the same type */
	public int[][] consShifts;
	/** a[i][j] == 1 iff shift j must not follow shift i */
	public boolean[][] forbiddenSequence;
	

}
