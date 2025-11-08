package data;

public class Week {
	
	/** Specifies the position of this week in the sequence. Not set by parser */
	public int index;
	
	/** minRequirements[day][shift][skill], order as in {@link Scenario} */
	public int[][][] minRequirements;
	/** optRequirements[day][shift][skill], order as defined in {@link Scenario} */	
	public int[][][] optRequirements;
	
	/** shiftOffRequested[i] = {nurse, day, shift}, where -1 is a request for a day off */
	public int[][] shiftOffRequested;
}