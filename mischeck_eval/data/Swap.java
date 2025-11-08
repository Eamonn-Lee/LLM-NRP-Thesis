package data;

public class Swap implements Move {
	
	private int nurse1;
	private int nurse2;
	private int blockSize;
	private int day;
	
	public Swap(){}
	
	public Swap(int nurse1, int nurse2, int blockSize, int day) {
		super();
		this.nurse1 = nurse1;
		this.nurse2 = nurse2;
		this.blockSize = blockSize;
		this.day = day;
	}
	
	public void setVal(int nurse1, int nurse2, int blockSize, int day){
		this.nurse1 = nurse1;
		this.nurse2 = nurse2;
		this.blockSize = blockSize;
		this.day = day;		
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + blockSize;
		result = prime * result + day;
		result = prime * result + nurse1;
		result = prime * result + nurse2;
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
		Swap other = (Swap) obj;
		if (blockSize != other.blockSize)
			return false;
		if (day != other.day)
			return false;
		if (nurse1 != other.nurse1)
			return false;
		if (nurse2 != other.nurse2)
			return false;
		return true;
	}

}
