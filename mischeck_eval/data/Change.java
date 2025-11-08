package data;

public class Change implements Move {

	private int nurse;
	private int day;
	private int newShift;
	private int newSkill;
	
	public Change(){}

	public Change(int nurse, int day, int newShift, int newSkill) {
		super();
		this.nurse = nurse;
		this.day = day;
		this.newShift = newShift;
		this.newSkill = newSkill;
	}

	public void setVal(int nurse, int day, int newShift, int newSkill){
		this.nurse = nurse;
		this.day = day;
		this.newShift = newShift;
		this.newSkill = newSkill;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + day;
		result = prime * result + newShift;
		result = prime * result + newSkill;
		result = prime * result + nurse;
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		Change other = (Change) obj;
		if (day != other.day)
			return false;
		if (newShift != other.newShift)
			return false;
		if (newSkill != other.newSkill)
			return false;
		if (nurse != other.nurse)
			return false;
		return true;
	}

}
