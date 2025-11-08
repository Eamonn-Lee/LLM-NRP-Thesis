package data;

public class History {
	
	public int[] totalAssignments;
	public int[] nrWorkingWeekends;
	/** contains the id of the last assigned shift (or -1 for a free day) */
	public int[] lastShift; 
	public int[] consecutiveShift;
	public int[] consecutiveWork;
	public int[] consecutiveFree;
	
	/** helper method that initializes all arrays to the same size */
	public void initAll(int nrNurses) {
		totalAssignments = new int[nrNurses];
		nrWorkingWeekends = new int[nrNurses];
		lastShift = new int[nrNurses];
		consecutiveShift = new int[nrNurses];
		consecutiveWork = new int[nrNurses];
		consecutiveFree = new int[nrNurses];
	}
}
