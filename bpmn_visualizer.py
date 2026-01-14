import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as lines

# The BPMN XML content (cleaned of citation tags for execution)
bpmn_xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" xmlns:camunda="http://camunda.org/schema/1.0/bpmn" id="Definitions_Turnaround_CV_Final" targetNamespace="http://bpmn.io/schema/bpmn" exporter="Camunda Modeler" exporterVersion="5.0.0">
  <bpmn:collaboration id="Collaboration_Turnaround_CV">
    <bpmn:participant id="Participant_GroundOps" name="Target Process: Aircraft Turnaround (Metadata included)" processRef="Process_Turnaround_CV" />
  </bpmn:collaboration>
  <bpmn:process id="Process_Turnaround_CV" isExecutable="false">
    <bpmn:laneSet id="LaneSet_Main">
      <bpmn:lane id="Lane_Gate" name="Gate &amp; Passenger Svc">
        <bpmn:flowNodeRef>StartEvent_OnBlock</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Gateway_Main_Split</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_Deboard</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_SecCheck</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_Board</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Gateway_Main_Join</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_Finalize</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>EndEvent_OffBlock</bpmn:flowNodeRef>
      </bpmn:lane>
      <bpmn:lane id="Lane_Ramp" name="Ramp &amp; Technical">
        <bpmn:flowNodeRef>Gateway_Ramp_Split</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_Unload</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_Load</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_Refuel</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_Walkaround</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_WaterWaste</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Gateway_Ramp_Join</bpmn:flowNodeRef>
      </bpmn:lane>
      <bpmn:lane id="Lane_Cabin" name="Cabin &amp; Service">
        <bpmn:flowNodeRef>Task_Cleaning</bpmn:flowNodeRef>
        <bpmn:flowNodeRef>Task_Catering</bpmn:flowNodeRef>
      </bpmn:lane>
    </bpmn:laneSet>
    <bpmn:startEvent id="StartEvent_OnBlock" name="Flugzeug On-Block">
      <bpmn:outgoing>Flow_1</bpmn:outgoing>
    </bpmn:startEvent>
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_OnBlock" targetRef="Gateway_Main_Split" />
    <bpmn:parallelGateway id="Gateway_Main_Split" name="Start Turnaround">
      <bpmn:incoming>Flow_1</bpmn:incoming>
      <bpmn:outgoing>Flow_Gate</bpmn:outgoing>
      <bpmn:outgoing>Flow_Ramp</bpmn:outgoing>
      <bpmn:outgoing>Flow_Cabin</bpmn:outgoing>
    </bpmn:parallelGateway>
    <bpmn:userTask id="Task_Deboard" name="Deboarding&#10;(ca. 15 min)">
      <bpmn:incoming>Flow_Gate</bpmn:incoming>
      <bpmn:outgoing>Flow_Deboard_Sec</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:userTask id="Task_SecCheck" name="Security Check&#10;(ca. 5 min)">
      <bpmn:incoming>Flow_Deboard_Sec</bpmn:incoming>
      <bpmn:outgoing>Flow_Sec_Board</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:userTask id="Task_Board" name="Boarding&#10;(ca. 20 min)">
      <bpmn:incoming>Flow_Sec_Board</bpmn:incoming>
      <bpmn:outgoing>Flow_Gate_Done</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:sequenceFlow id="Flow_Gate" sourceRef="Gateway_Main_Split" targetRef="Task_Deboard" />
    <bpmn:sequenceFlow id="Flow_Deboard_Sec" sourceRef="Task_Deboard" targetRef="Task_SecCheck" />
    <bpmn:sequenceFlow id="Flow_Sec_Board" sourceRef="Task_SecCheck" targetRef="Task_Board" />
    <bpmn:sequenceFlow id="Flow_Gate_Done" sourceRef="Task_Board" targetRef="Gateway_Main_Join" />
    <bpmn:sequenceFlow id="Flow_Ramp" sourceRef="Gateway_Main_Split" targetRef="Gateway_Ramp_Split" />
    <bpmn:parallelGateway id="Gateway_Ramp_Split" name="Start Ramp Ops">
      <bpmn:incoming>Flow_Ramp</bpmn:incoming>
      <bpmn:outgoing>Flow_R_Unload</bpmn:outgoing>
      <bpmn:outgoing>Flow_R_Refuel</bpmn:outgoing>
      <bpmn:outgoing>Flow_R_Walk</bpmn:outgoing>
      <bpmn:outgoing>Flow_R_Water</bpmn:outgoing>
    </bpmn:parallelGateway>
    <bpmn:manualTask id="Task_Unload" name="Unloading&#10;(ca. 20 min)">
      <bpmn:incoming>Flow_R_Unload</bpmn:incoming>
      <bpmn:outgoing>Flow_Unload_Load</bpmn:outgoing>
    </bpmn:manualTask>
    <bpmn:manualTask id="Task_Load" name="Loading&#10;(ca. 25 min)">
      <bpmn:incoming>Flow_Unload_Load</bpmn:incoming>
      <bpmn:outgoing>Flow_Load_Done</bpmn:outgoing>
    </bpmn:manualTask>
    <bpmn:manualTask id="Task_Refuel" name="Refueling&#10;(ca. 15 min)">
      <bpmn:incoming>Flow_R_Refuel</bpmn:incoming>
      <bpmn:outgoing>Flow_Refuel_Done</bpmn:outgoing>
    </bpmn:manualTask>
    <bpmn:manualTask id="Task_Walkaround" name="Walk-around&#10;(ca. 10 min)">
      <bpmn:incoming>Flow_R_Walk</bpmn:incoming>
      <bpmn:outgoing>Flow_Walk_Done</bpmn:outgoing>
    </bpmn:manualTask>
    <bpmn:manualTask id="Task_WaterWaste" name="Water &amp; Waste&#10;(ca. 10 min)">
      <bpmn:incoming>Flow_R_Water</bpmn:incoming>
      <bpmn:outgoing>Flow_Water_Done</bpmn:outgoing>
    </bpmn:manualTask>
    <bpmn:parallelGateway id="Gateway_Ramp_Join" name="Ramp Ops Done">
      <bpmn:incoming>Flow_Load_Done</bpmn:incoming>
      <bpmn:incoming>Flow_Refuel_Done</bpmn:incoming>
      <bpmn:incoming>Flow_Walk_Done</bpmn:incoming>
      <bpmn:incoming>Flow_Water_Done</bpmn:incoming>
      <bpmn:outgoing>Flow_Ramp_Done</bpmn:outgoing>
    </bpmn:parallelGateway>
    <bpmn:sequenceFlow id="Flow_R_Unload" sourceRef="Gateway_Ramp_Split" targetRef="Task_Unload" />
    <bpmn:sequenceFlow id="Flow_Unload_Load" sourceRef="Task_Unload" targetRef="Task_Load" />
    <bpmn:sequenceFlow id="Flow_R_Refuel" sourceRef="Gateway_Ramp_Split" targetRef="Task_Refuel" />
    <bpmn:sequenceFlow id="Flow_R_Walk" sourceRef="Gateway_Ramp_Split" targetRef="Task_Walkaround" />
    <bpmn:sequenceFlow id="Flow_R_Water" sourceRef="Gateway_Ramp_Split" targetRef="Task_WaterWaste" />
    <bpmn:sequenceFlow id="Flow_Load_Done" sourceRef="Task_Load" targetRef="Gateway_Ramp_Join" />
    <bpmn:sequenceFlow id="Flow_Refuel_Done" sourceRef="Task_Refuel" targetRef="Gateway_Ramp_Join" />
    <bpmn:sequenceFlow id="Flow_Walk_Done" sourceRef="Task_Walkaround" targetRef="Gateway_Ramp_Join" />
    <bpmn:sequenceFlow id="Flow_Water_Done" sourceRef="Task_WaterWaste" targetRef="Gateway_Ramp_Join" />
    <bpmn:sequenceFlow id="Flow_Ramp_Done" sourceRef="Gateway_Ramp_Join" targetRef="Gateway_Main_Join" />
    <bpmn:sequenceFlow id="Flow_Cabin" sourceRef="Gateway_Main_Split" targetRef="Task_Cleaning" />
    <bpmn:manualTask id="Task_Cleaning" name="Cleaning&#10;(ca. 15 min)">
      <bpmn:incoming>Flow_Cabin</bpmn:incoming>
      <bpmn:outgoing>Flow_Clean_Cater</bpmn:outgoing>
    </bpmn:manualTask>
    <bpmn:manualTask id="Task_Catering" name="Catering&#10;(ca. 15 min)">
      <bpmn:incoming>Flow_Clean_Cater</bpmn:incoming>
      <bpmn:outgoing>Flow_Cabin_Done</bpmn:outgoing>
    </bpmn:manualTask>
    <bpmn:sequenceFlow id="Flow_Clean_Cater" sourceRef="Task_Cleaning" targetRef="Task_Catering" />
    <bpmn:sequenceFlow id="Flow_Cabin_Done" sourceRef="Task_Catering" targetRef="Gateway_Main_Join" />
    <bpmn:parallelGateway id="Gateway_Main_Join" name="Ready for Departure">
      <bpmn:incoming>Flow_Gate_Done</bpmn:incoming>
      <bpmn:incoming>Flow_Ramp_Done</bpmn:incoming>
      <bpmn:incoming>Flow_Cabin_Done</bpmn:incoming>
      <bpmn:outgoing>Flow_To_Final</bpmn:outgoing>
    </bpmn:parallelGateway>
    <bpmn:userTask id="Task_Finalize" name="Doors Closed &amp;&#10;Off-Block Approval">
      <bpmn:incoming>Flow_To_Final</bpmn:incoming>
      <bpmn:outgoing>Flow_End</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:sequenceFlow id="Flow_To_Final" sourceRef="Gateway_Main_Join" targetRef="Task_Finalize" />
    <bpmn:endEvent id="EndEvent_OffBlock" name="Flugzeug Off-Block">
      <bpmn:incoming>Flow_End</bpmn:incoming>
    </bpmn:endEvent>
    <bpmn:sequenceFlow id="Flow_End" sourceRef="Task_Finalize" targetRef="EndEvent_OffBlock" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Collaboration_Turnaround_CV">
      <bpmndi:BPMNShape id="Participant_Shape" bpmnElement="Participant_GroundOps" isHorizontal="true">
        <dc:Bounds x="120" y="80" width="1450" height="780" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Lane_Gate_Shape" bpmnElement="Lane_Gate" isHorizontal="true">
        <dc:Bounds x="150" y="80" width="1420" height="220" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Lane_Ramp_Shape" bpmnElement="Lane_Ramp" isHorizontal="true">
        <dc:Bounds x="150" y="300" width="1420" height="420" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Lane_Cabin_Shape" bpmnElement="Lane_Cabin" isHorizontal="true">
        <dc:Bounds x="150" y="720" width="1420" height="140" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="StartEvent_di" bpmnElement="StartEvent_OnBlock">
        <dc:Bounds x="210" y="172" width="36" height="36" />
        <bpmndi:BPMNLabel><dc:Bounds x="190" y="215" width="76" height="27" /></bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Gateway_Main_Split_di" bpmnElement="Gateway_Main_Split">
        <dc:Bounds x="300" y="165" width="50" height="50" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task_Deboard_di" bpmnElement="Task_Deboard">
        <dc:Bounds x="430" y="150" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task_SecCheck_di" bpmnElement="Task_SecCheck">
        <dc:Bounds x="590" y="150" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task_Board_di" bpmnElement="Task_Board">
        <dc:Bounds x="750" y="150" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Gateway_Ramp_Split_di" bpmnElement="Gateway_Ramp_Split">
        <dc:Bounds x="430" y="485" width="50" height="50" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task_Unload_di" bpmnElement="Task_Unload">
        <dc:Bounds x="550" y="320" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task_Load_di" bpmnElement="Task_Load">
        <dc:Bounds x="780" y="320" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task_Refuel_di" bpmnElement="Task_Refuel">
        <dc:Bounds x="650" y="420" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task_Walk_di" bpmnElement="Task_Walkaround">
        <dc:Bounds x="550" y="530" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task_Water_di" bpmnElement="Task_WaterWaste">
        <dc:Bounds x="780" y="620" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Gateway_Ramp_Join_di" bpmnElement="Gateway_Ramp_Join">
        <dc:Bounds x="950" y="485" width="50" height="50" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task_Cleaning_di" bpmnElement="Task_Cleaning">
        <dc:Bounds x="430" y="750" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task_Catering_di" bpmnElement="Task_Catering">
        <dc:Bounds x="650" y="750" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Gateway_Main_Join_di" bpmnElement="Gateway_Main_Join">
        <dc:Bounds x="1100" y="165" width="50" height="50" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task_Finalize_di" bpmnElement="Task_Finalize">
        <dc:Bounds x="1200" y="150" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndEvent_OffBlock_di" bpmnElement="EndEvent_OffBlock">
        <dc:Bounds x="1350" y="172" width="36" height="36" />
        <bpmndi:BPMNLabel><dc:Bounds x="1333" y="215" width="71" height="27" /></bpmndi:BPMNLabel>
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="Edge_1" bpmnElement="Flow_1"><di:waypoint x="246" y="190" /><di:waypoint x="300" y="190" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Gate" bpmnElement="Flow_Gate"><di:waypoint x="350" y="190" /><di:waypoint x="430" y="190" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Ramp_Split" bpmnElement="Flow_Ramp"><di:waypoint x="325" y="215" /><di:waypoint x="325" y="510" /><di:waypoint x="430" y="510" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Cabin_Split" bpmnElement="Flow_Cabin"><di:waypoint x="325" y="215" /><di:waypoint x="325" y="790" /><di:waypoint x="430" y="790" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_G1" bpmnElement="Flow_Deboard_Sec"><di:waypoint x="530" y="190" /><di:waypoint x="590" y="190" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_G2" bpmnElement="Flow_Sec_Board"><di:waypoint x="690" y="190" /><di:waypoint x="750" y="190" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_G3" bpmnElement="Flow_Gate_Done"><di:waypoint x="850" y="190" /><di:waypoint x="1100" y="190" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_RU" bpmnElement="Flow_R_Unload"><di:waypoint x="455" y="485" /><di:waypoint x="455" y="360" /><di:waypoint x="550" y="360" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_UL" bpmnElement="Flow_Unload_Load"><di:waypoint x="650" y="360" /><di:waypoint x="780" y="360" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_RR" bpmnElement="Flow_R_Refuel"><di:waypoint x="455" y="510" /><di:waypoint x="560" y="510" /><di:waypoint x="560" y="460" /><di:waypoint x="650" y="460" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_RW" bpmnElement="Flow_R_Walk"><di:waypoint x="455" y="535" /><di:waypoint x="455" y="570" /><di:waypoint x="550" y="570" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_RWW" bpmnElement="Flow_R_Water"><di:waypoint x="455" y="535" /><di:waypoint x="455" y="660" /><di:waypoint x="780" y="660" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_J1" bpmnElement="Flow_Load_Done"><di:waypoint x="880" y="360" /><di:waypoint x="975" y="360" /><di:waypoint x="975" y="485" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_J2" bpmnElement="Flow_Refuel_Done"><di:waypoint x="750" y="460" /><di:waypoint x="975" y="460" /><di:waypoint x="975" y="485" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_J3" bpmnElement="Flow_Walk_Done"><di:waypoint x="650" y="570" /><di:waypoint x="975" y="570" /><di:waypoint x="975" y="535" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_J4" bpmnElement="Flow_Water_Done"><di:waypoint x="880" y="660" /><di:waypoint x="975" y="660" /><di:waypoint x="975" y="535" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_J5" bpmnElement="Flow_Ramp_Done"><di:waypoint x="1000" y="510" /><di:waypoint x="1125" y="510" /><di:waypoint x="1125" y="215" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_C1" bpmnElement="Flow_Clean_Cater"><di:waypoint x="530" y="790" /><di:waypoint x="650" y="790" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_C2" bpmnElement="Flow_Cabin_Done"><di:waypoint x="750" y="790" /><di:waypoint x="1125" y="790" /><di:waypoint x="1125" y="215" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_Fin" bpmnElement="Flow_To_Final"><di:waypoint x="1150" y="190" /><di:waypoint x="1200" y="190" /></bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Edge_End" bpmnElement="Flow_End"><di:waypoint x="1300" y="190" /><di:waypoint x="1350" y="190" /></bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>
"""


def visualize_bpmn(xml_string):
    # Namespaces usually found in BPMN
    ns = {
        'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
        'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
        'dc': 'http://www.omg.org/spec/DD/20100524/DC',
        'di': 'http://www.omg.org/spec/DD/20100524/DI'
    }

    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return

    # Extract Process Elements to map IDs to Names and Types
    elements = {}
    process = root.find('.//bpmn:process', ns)
    if process is not None:
        for child in process:
            # We care about tasks, events, gateways, lanes
            tag = child.tag.split('}')[-1]  # strip namespace
            eid = child.get('id')
            name = child.get('name', '')
            elements[eid] = {'type': tag, 'name': name}

    # Extract Lane information for background drawing
    lanes = []
    lane_sets = process.findall('.//bpmn:lane', ns)
    for lane in lane_sets:
        eid = lane.get('id')
        name = lane.get('name', '')
        elements[eid] = {'type': 'lane', 'name': name}

    # Setup Plot
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.invert_yaxis()  # BPMN coords are usually top-left origin, matplotlib is bottom-left
    ax.set_aspect('equal')
    ax.axis('off')

    # Parse Diagram Information (DI)
    diagram = root.find('.//bpmndi:BPMNPlane', ns)

    # 1. Draw Lanes (Background)
    # We iterate twice to ensure lanes are drawn first (behind tasks)
    for shape in diagram.findall('bpmndi:BPMNShape', ns):
        bpmn_id = shape.get('bpmnElement')
        bounds = shape.find('dc:Bounds', ns)

        if bounds is not None and bpmn_id in elements:
            x = float(bounds.get('x'))
            y = float(bounds.get('y'))
            w = float(bounds.get('width'))
            h = float(bounds.get('height'))

            el_type = elements[bpmn_id]['type']

            if el_type == 'participant' or el_type == 'lane':
                # Draw Swimlane/Pool
                rect = patches.Rectangle((x, y), w, h, linewidth=1, edgecolor='#999', facecolor='#f4f4f4', zorder=0)
                ax.add_patch(rect)
                # Label the lane (rotated on the left usually, but we'll put it top-left)
                ax.text(x + 20, y + h / 2, elements[bpmn_id]['name'], rotation=90, verticalalignment='center',
                        fontsize=9, color='#555')

    # 2. Draw Edges (Sequence Flows)
    for edge in diagram.findall('bpmndi:BPMNEdge', ns):
        waypoints = edge.findall('di:waypoint', ns)
        x_coords = [float(wp.get('x')) for wp in waypoints]
        y_coords = [float(wp.get('y')) for wp in waypoints]

        ax.plot(x_coords, y_coords, color='#333', linewidth=1.5, zorder=1)
        # Draw Arrow Head at the end
        if len(x_coords) >= 2:
            ax.annotate('', xy=(x_coords[-1], y_coords[-1]), xytext=(x_coords[-2], y_coords[-2]),
                        arrowprops=dict(arrowstyle='->', lw=1.5, color='#333'), zorder=1)

    # 3. Draw Flow Nodes (Tasks, Gateways, Events)
    for shape in diagram.findall('bpmndi:BPMNShape', ns):
        bpmn_id = shape.get('bpmnElement')
        bounds = shape.find('dc:Bounds', ns)

        if bounds is not None and bpmn_id in elements:
            x = float(bounds.get('x'))
            y = float(bounds.get('y'))
            w = float(bounds.get('width'))
            h = float(bounds.get('height'))

            el_data = elements[bpmn_id]
            el_type = el_data['type']
            name = el_data['name']

            # Skip participants/lanes (already drawn)
            if el_type in ['participant', 'lane']:
                continue

            center_x = x + w / 2
            center_y = y + h / 2

            if 'Task' in el_type:
                # Rounded Rectangle for Tasks
                box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                             linewidth=1.5, edgecolor='#0052cc', facecolor='white', zorder=2)
                ax.add_patch(box)
                ax.text(center_x, center_y, name, ha='center', va='center', fontsize=8, wrap=True)

            elif 'Gateway' in el_type:
                # Diamond for Gateways
                diamond = patches.Polygon([[center_x, y], [x + w, center_y], [center_x, y + h], [x, center_y]],
                                          closed=True, linewidth=1.5, edgecolor='#cc9900', facecolor='white', zorder=2)
                ax.add_patch(diamond)
                # Gateway labels are often external, but we'll try to place them nearby if not empty
                if name:
                    ax.text(center_x, y - 15, name, ha='center', fontsize=7, style='italic')

            elif 'Event' in el_type:
                # Circle for Events
                radius = min(w, h) / 2
                circle = patches.Circle((center_x, center_y), radius, linewidth=1.5, edgecolor='#cc0000',
                                        facecolor='white', zorder=2)
                ax.add_patch(circle)
                # Bold border for End Event
                if 'End' in el_type:
                    circle.set_linewidth(3)
                ax.text(center_x, y + h + 15, name, ha='center', fontsize=8)

    plt.title(
        "BPMN Process Visualization: " + elements.get('Process_Turnaround_CV', {}).get('name', 'Turnaround Process'),
        fontsize=14)
    plt.tight_layout()
    plt.show()


# Run the visualization
visualize_bpmn(bpmn_xml_content)