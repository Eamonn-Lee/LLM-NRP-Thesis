import java.io.FileInputStream;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

import data.Contract;
import data.Nurse;
import data.Scenario;

public class ScenarioParser {

    private JSONObject jsonRoot;

    public ScenarioParser(String instanceName) {
        this(instanceName, "../json_Dataset/");
    }

    public ScenarioParser(String instanceName, String path) {
        String filename = "Sc-" + instanceName + ".json";
        try (FileInputStream fis = new FileInputStream(path + instanceName + "/" + filename)) {
            JSONTokener tokener = new JSONTokener(fis);
            jsonRoot = new JSONObject(tokener);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public Scenario parse() {
        Scenario sc = new Scenario();

        sc.nrWeeks = jsonRoot.getInt("numberOfWeeks");

        // Skills
        JSONArray skillsArr = jsonRoot.getJSONArray("skills");
        sc.skills = new String[skillsArr.length()];
        for (int i = 0; i < skillsArr.length(); i++) {
            sc.skills[i] = skillsArr.getString(i);
        }

        // Shift Types
        JSONArray shiftTypes = jsonRoot.getJSONArray("shiftTypes");
        sc.shifts = new String[shiftTypes.length()];
        sc.consShifts = new int[shiftTypes.length()][2];
        for (int i = 0; i < shiftTypes.length(); i++) {
            JSONObject shift = shiftTypes.getJSONObject(i);
            sc.shifts[i] = shift.getString("id");
            sc.consShifts[i][0] = shift.getInt("minimumNumberOfConsecutiveAssignments");
            sc.consShifts[i][1] = shift.getInt("maximumNumberOfConsecutiveAssignments");
        }

        // Forbidden Shift Type Successions
        sc.forbiddenSequence = new boolean[sc.shifts.length][sc.shifts.length];
        List<String> shiftList = Arrays.asList(sc.shifts);
        JSONArray forbids = jsonRoot.getJSONArray("forbiddenShiftTypeSuccessions");
        for (int i = 0; i < forbids.length(); i++) {
            JSONObject rule = forbids.getJSONObject(i);
            int prevId = shiftList.indexOf(rule.getString("precedingShiftType"));
            JSONArray successors = rule.getJSONArray("succeedingShiftTypes");
            for (int j = 0; j < successors.length(); j++) {
                int succId = shiftList.indexOf(successors.getString(j));
                sc.forbiddenSequence[prevId][succId] = true;
            }
        }

        // Contracts
        JSONArray contracts = jsonRoot.getJSONArray("contracts");
        for (int i = 0; i < contracts.length(); i++) {
            Contract c = parseContract(contracts.getJSONObject(i));
            sc.contracts.put(c.id, c);
        }

        // Nurses
        JSONArray nurses = jsonRoot.getJSONArray("nurses");
        sc.nurseIDs = new String[nurses.length()];
        sc.nurses = new Nurse[nurses.length()];
        for (int i = 0; i < nurses.length(); i++) {
            Nurse n = parseNurse(nurses.getJSONObject(i), sc);
            sc.nurses[i] = n;
            sc.nurseIDs[i] = n.id;
        }

        return sc;
    }

    private Contract parseContract(JSONObject json) {
        Contract c = new Contract();
        c.id = json.getString("id");

        c.minAssignments = json.getInt("minimumNumberOfAssignments");
        c.maxAssignments = json.getInt("maximumNumberOfAssignments");

        c.minConsWork = json.getInt("minimumNumberOfConsecutiveWorkingDays");
        c.maxConsWork = json.getInt("maximumNumberOfConsecutiveWorkingDays");

        c.minConsFree = json.getInt("minimumNumberOfConsecutiveDaysOff");
        c.maxConsFree = json.getInt("maximumNumberOfConsecutiveDaysOff");

        c.maxWeekends = json.getInt("maximumNumberOfWorkingWeekends");

        // JSON has 0/1; we convert it to boolean
        c.completeWeekend = json.getInt("completeWeekends") == 1;

        return c;
    }

    private Nurse parseNurse(JSONObject json, Scenario sc) {
        Nurse n = new Nurse();
        n.id = json.getString("id");
        n.contract = sc.contracts.get(json.getString("contract"));

        JSONArray skillArray = json.getJSONArray("skills");
        List<String> skills = Arrays.asList(sc.skills);
        n.skills = new boolean[sc.skills.length];
        n.skillList = new int[skillArray.length()];

        for (int i = 0; i < skillArray.length(); i++) {
            String skill = skillArray.getString(i);
            int skillId = skills.indexOf(skill);
            if (skillId != -1) {
                n.skills[skillId] = true;
                n.skillList[i] = skillId;
            }
        }

        return n;
    }
}
