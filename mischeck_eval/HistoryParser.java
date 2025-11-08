import java.io.FileInputStream;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

import data.History;
import data.Scenario;

public class HistoryParser {
    private JSONObject jsonRoot;
    private Scenario sc;

    public HistoryParser(String instanceName, int historyID, Scenario sc) {
        this(instanceName, historyID, sc, "../json_Dataset/");
    }

    public HistoryParser(String instanceName, int historyID, Scenario sc, String path) {
        this.sc = sc;
        String filename = "H0-" + instanceName + "-" + historyID + ".json";

        try (FileInputStream fis = new FileInputStream(path + instanceName + "/" + filename)) {
            JSONTokener tokener = new JSONTokener(fis);
            jsonRoot = new JSONObject(tokener);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public History parse() {
        History h = new History();

        List<String> nurseList = Arrays.asList(sc.nurseIDs);
        List<String> shiftList = Arrays.asList(sc.shifts);

        h.initAll(sc.nurseIDs.length);

        JSONArray nurseHistories = jsonRoot.getJSONArray("nurseHistory");
        for (int i = 0; i < nurseHistories.length(); i++) {
            JSONObject nurseHistory = nurseHistories.getJSONObject(i);

            String nurseName = nurseHistory.getString("nurse");
            int nurseID = nurseList.indexOf(nurseName);
            if (nurseID == -1) continue; // safety check

            h.totalAssignments[nurseID] = nurseHistory.getInt("numberOfAssignments");
            h.nrWorkingWeekends[nurseID] = nurseHistory.getInt("numberOfWorkingWeekends");

            String lastShift = nurseHistory.getString("lastAssignedShiftType");
            h.lastShift[nurseID] = lastShift.equals("None") ? -1 : shiftList.indexOf(lastShift);

            h.consecutiveShift[nurseID] = nurseHistory.getInt("numberOfConsecutiveAssignments");
            h.consecutiveWork[nurseID] = nurseHistory.getInt("numberOfConsecutiveWorkingDays");
            h.consecutiveFree[nurseID] = nurseHistory.getInt("numberOfConsecutiveDaysOff");
        }

        return h;
    }
}
