package data;

public class Nurse {

	public String id;
	public Contract contract;
	public boolean[] skills; //skills[i] is true iff the nurse has the skill with id i
	public int[] skillList; //as above, but indices of skills stored in array
	
}
