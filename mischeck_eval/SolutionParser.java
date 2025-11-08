import java.io.FileInputStream;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

import data.Scenario;

public class SolutionParser {

    public int[][] shiftAssignment;
    public int[][] skillAssignment;

    private Scenario sc;
    private JSONObject jsonRoot;

    public SolutionParser(String filename, Scenario sc) {
        this(filename, sc, "../");
    }

    public SolutionParser(String filename, Scenario sc, String path) {
        this.sc = sc;

        try (FileInputStream fis = new FileInputStream(path + filename)) {
            JSONTokener tokener = new JSONTokener(fis);
            jsonRoot = new JSONObject(tokener);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void parse() {
        int numNurses = sc.nurseIDs.length;
        shiftAssignment = new int[numNurses][7];
        skillAssignment = new int[numNurses][7];

        for (int i = 0; i < numNurses; i++) {
            Arrays.fill(shiftAssignment[i], -1);
            Arrays.fill(skillAssignment[i], 0);
        }

        List<String> nurseList = Arrays.asList(sc.nurseIDs);
        List<String> shiftList = Arrays.asList(sc.shifts);
        List<String> skillList = Arrays.asList(sc.skills);
        List<String> days = Arrays.asList("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun");

        JSONArray assignments = jsonRoot.getJSONArray("assignments");
        for (int i = 0; i < assignments.length(); i++) {
            JSONObject a = assignments.getJSONObject(i);

            int nurseID = nurseList.indexOf(a.getString("nurse"));
            int dayID = days.indexOf(a.getString("day"));
            int shiftID = shiftList.indexOf(a.getString("shiftType"));
            int skillID = skillList.indexOf(a.getString("skill"));

            if (nurseID != -1 && dayID != -1 && shiftID != -1 && skillID != -1) {
                shiftAssignment[nurseID][dayID] = shiftID;
                skillAssignment[nurseID][dayID] = skillID;
            }
        }
    }
}
