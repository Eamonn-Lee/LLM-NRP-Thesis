import java.io.File;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.w3c.dom.Document;
import org.w3c.dom.Element;

import data.Scenario;

public class SolutionWriter {

	private Scenario sc;
	private String instanceName;

	private static String[] days = new String[]{"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"};

	public SolutionWriter(Scenario sc, String instanceName) {
		this.sc = sc;
		this.instanceName = instanceName;
	}

	public void print(int[][] shiftAssignment, int[][] skillAssignment, String weekID, int index){

		try {

			DocumentBuilderFactory docFactory = DocumentBuilderFactory.newInstance();
			DocumentBuilder docBuilder = docFactory.newDocumentBuilder();

			// root elements
			Document doc = docBuilder.newDocument();
			Element rootElement = doc.createElement("Solution");
			doc.appendChild(rootElement);
			String namespaceURL = "http://www.w3.org/2001/XMLSchema-instance";
			rootElement.setAttributeNS(namespaceURL, "xsi:noNamespaceSchemaLocation", "Solution.xsd");

			Element weekElem = doc.createElement("Week");
			weekElem.appendChild(doc.createTextNode(""+index));
			rootElement.appendChild(weekElem);

			Element instanceElem = doc.createElement("Scenario");
			instanceElem.appendChild(doc.createTextNode(instanceName));
			rootElement.appendChild(instanceElem);

			Element assignmentsElem = doc.createElement("Assignments");
			rootElement.appendChild(assignmentsElem);

			for(int nurse = 0; nurse < sc.nurses.length; nurse++){
				for(int day = 0; day < 7; day++){
					if(shiftAssignment[nurse][day] >= 0){
						Element assignElem = doc.createElement("Assignment");

						Element nurseElem = doc.createElement("Nurse");
						nurseElem.appendChild(doc.createTextNode(sc.nurseIDs[nurse]));
						assignElem.appendChild(nurseElem);

						Element dayElem = doc.createElement("Day");
						dayElem.appendChild(doc.createTextNode(days[day]));
						assignElem.appendChild(dayElem);

						Element shiftElem = doc.createElement("ShiftType");
						shiftElem.appendChild(doc.createTextNode(sc.shifts[shiftAssignment[nurse][day]]));
						assignElem.appendChild(shiftElem);

						Element skillElem = doc.createElement("Skill");
						skillElem.appendChild(doc.createTextNode(sc.skills[skillAssignment[nurse][day]]));
						assignElem.appendChild(skillElem);

						assignmentsElem.appendChild(assignElem);
					}
				}
			}

			// write the content into xml file
			String filename = "Solutions/"+instanceName+"/Sol-"+instanceName+"-"+weekID+"-"+index+".xml";
			TransformerFactory transformerFactory = TransformerFactory.newInstance();
			Transformer transformer = transformerFactory.newTransformer();
			transformer.setOutputProperty(OutputKeys.INDENT, "yes");
			transformer.setOutputProperty("{http://xml.apache.org/xslt}indent-amount", "2");			
			DOMSource source = new DOMSource(doc);
			StreamResult result = new StreamResult(new File(filename));

			// Output to console for testing
			//StreamResult result = new StreamResult(System.out);

			transformer.transform(source, result);

			System.out.println("File saved!");

		} catch (ParserConfigurationException pce) {
			pce.printStackTrace();
		} catch (TransformerException tfe) {
			tfe.printStackTrace();
		}
	}

}
