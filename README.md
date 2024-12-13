# **FreeCAD Workbench for Parametric Surface Mine Design 🚧⛏️**

## **Overview**

This workbench is under active development. As each feature is completed, there will be a link added, providing detailed documentation on how the feature works. Links will point to additional markdown files located in the `descriptions` folder.

---

## **Features 🌟**

- **Parametric Toes and Crests Generation ✅**  
  - Updated detailed toolset description is available [here](descriptions/pit_design_no_ramps.md)
  - Create toes and crests based on user-defined parameters and an optimization shell (developed).  
  - Generate toes and crests from user-defined parameters and a freehanded pit bottom sketch (developed).
  
- **Mine Slope Design online tool (Done)**  
  - This is a tool to design pit slope and to calculate parameters to meet the target slope angle. I have incorporated it with FreeCAD workbench. The tool description is on my LinkedIn [page:](https://www.linkedin.com/feed/update/urn:li:activity:7250442808824664065/) ✅

- **OMF Integration (Not started)**  
  - Full OMF integration for importing, exporting, and browsing data using [OMF Python](https://github.com/gmggroup/omf-python) (import is implemented).

- **Block Modeling Tool (Not started)**  
  - Regular block modeling browsing and visualization tool (implemented, may require serialization process optimization)

  *Official documentation for OMF and block modelling is not ready yet, but there is relatively good description on my LinkedIn [article](https://www.linkedin.com/pulse/open-source-freecad-workbench-parametric-pit-design-drop-mikulich-nmtre)*
  
- **Pit Optimization (Not started)**  
  - Incorporate withtin the workbench an optimization open-source tool by [Matthew Deutsch](https://github.com/MineFlowCSM/MineFlow) to calculate ultimate pit limits. Detailed description is [here](https://github.com/MineFlowCSM/MineFlow/blob/df0f30aabea494371704a926ba47f6166631774d/deutsch2022mineflow.pdf) (not started)
  - Create UX for user to fill up basic optimization parameters needed to calculate a value for each block.
  - Loop process over a list of different material prices in order to enable RAF analysis

- **Ramp Design 🚦(Not started)**  
  - Planned feature to enable the design of ramps (not started)
  - I am not sure how to tackle it in the right way just yet, so shifted it down. Contributors needed

- **Ramp Layout Optimization (Not started)**  
  - Layout ramps based on KPIs and Design of Experiments (DOE) principles (not started)

- **Block Modeling Tool (Not started)**  
  - Regular block modeling browsing and visualization tool (Not sure about this yet! 🤷‍♂️🤔)
