import java.io.FileInputStream;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

import data.Scenario;
import data.Week;

public class WeekParser {

    private JSONObject jsonRoot;
    private Scenario sc;

    public WeekParser(String instanceName, String weekID, Scenario sc) {
        this(instanceName, weekID, sc, "../json_Dataset/");
    }

    public WeekParser(String instanceName, String weekID, Scenario sc, String path) {
        this.sc = sc;
        String filename = "WD-" + instanceName + "-" + weekID + ".json";
        try (FileInputStream fis = new FileInputStream(path + instanceName + "/" + filename)) {
            JSONTokener tokener = new JSONTokener(fis);
            jsonRoot = new JSONObject(tokener);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public Week parse() {
        Week w = new Week();

        List<String> shiftList = Arrays.asList(sc.shifts);
        List<String> skillList = Arrays.asList(sc.skills);
        List<String> nurseList = Arrays.asList(sc.nurseIDs);
        List<String> days = Arrays.asList("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday");

        w.minRequirements = new int[7][sc.shifts.length][sc.skills.length];
        w.optRequirements = new int[7][sc.shifts.length][sc.skills.length];

        JSONArray requirements = jsonRoot.getJSONArray("requirements");
        for (int i = 0; i < requirements.length(); i++) {
            JSONObject req = requirements.getJSONObject(i);
            String shiftName = req.getString("shiftType");
            String skillName = req.getString("skill");

            int shift = shiftList.indexOf(shiftName);
            int skill = skillList.indexOf(skillName);

            for (int d = 0; d < 7; d++) {
                String dayKey = "requirementOn" + days.get(d);
                if (req.has(dayKey)) {
                    JSONObject reqDay = req.getJSONObject(dayKey);
                    int min = reqDay.getInt("minimum");
                    int opt = reqDay.getInt("optimal");
                    w.minRequirements[d][shift][skill] = min;
                    w.optRequirements[d][shift][skill] = opt;
                }
            }
        }

        JSONArray offRequests = jsonRoot.getJSONArray("shiftOffRequests");
        w.shiftOffRequested = new int[offRequests.length()][3];

        for (int i = 0; i < offRequests.length(); i++) {
            JSONObject req = offRequests.getJSONObject(i);

            int nurseID = nurseList.indexOf(req.getString("nurse"));
            int dayID = days.indexOf(req.getString("day"));

            String shiftName = req.getString("shiftType");
            int shiftID = shiftName.equals("Any") ? -1 : shiftList.indexOf(shiftName);

            w.shiftOffRequested[i] = new int[]{nurseID, dayID, shiftID};
        }

        return w;
    }
}
