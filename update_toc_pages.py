import re

# Exact Page Mapping from the 49-page PDF
TOC_DATA = [
    ["CHAPTER", "TITLE", "PAGE NOs"],
    ["", "ABSTRACT", "ii"],
    ["", "LIST OF TABLES", "iv"],
    ["", "LIST OF FIGURES", "v"],
    ["", "LIST OF ABBREVIATIONS", "vi"],
    ["1", "INTRODUCTION", "9"],
    ["1.1", "Introduction (Background)", "9"],
    ["1.2", "Problem Statement", "10"],
    ["1.3", "Objectives", "11"],
    ["1.4", "Contributions", "12"],
    ["2", "RELATED WORK", "14"],
    ["2.1", "Comprehensive Survey", "14"],
    ["2.2", "Summary and Findings of 2.1 in Tabular Format", "16"],
    ["2.3", "Challenges", "18"],
    ["2.4", "Motivation of the Project Work", "19"],
    ["3", "MATERIALS AND METHODS", "20"],
    ["3.1", "Mathematical Modelling / Datasets Description", "20"],
    ["3.2", "Method(s) of Mathematical Modelling / Data Processing", "24"],
    ["3.3", "Programming Tools Details", "26"],
    ["4", "METHODOLOGY", "28"],
    ["4.1", "Controller / Algorithm Design (Mathematical Equations with Description)", "28"],
    ["4.2", "Controller / Algorithm Design Steps", "31"],
    ["4.3", "Project Architecture", "32"],
    ["4.4", "Stability / Algorithm Analysis", "34"],
    ["4.5", "Project Complete Flowchart", "36"],
    ["5", "RESULTS AND DISCUSSION", "37"],
    ["5.1", "Simulation Setup", "37"],
    ["5.2", "Qualitative Results", "38"],
    ["5.3", "Quantitative Results", "39"],
    ["5.4", "Discussion", "44"],
    ["6", "CONCLUSION AND FUTURE DIRECTIONS", "46"],
    ["6.1", "Conclusion", "46"],
    ["6.2", "Future Directions", "46"],
    ["7", "REFERENCES", "48"]
]

TABLES_LIST = [
    ("TABLE I", "Summary of surveyed approaches in agricultural robotics and disease detection", "16"),
    ("TABLE II", "Pioneer 3-DX robot platform and kinematic parameters", "21"),
    ("TABLE III", "Sensor suite and perception specifications", "22"),
    ("TABLE IV", "Complete 7-row crop bed registry and field geometry", "23"),
    ("TABLE V", "Programming tools, libraries, and software environment", "26"),
    ("TABLE VI", "Main navigation, aiming, and spraying controller parameters", "30"),
    ("TABLE VII", "Main source modules and software components", "33"),
    ("TABLE VIII", "Webots simulation environment and physical setup parameters", "37"),
    ("TABLE IX", "Overall field inspection and precision spraying performance summary", "39"),
    ("TABLE X", "Detailed row-by-row inspection performance breakdown", "40"),
    ("TABLE XI", "EfficientNet-B0 confusion matrix and per-class performance metrics", "41"),
    ("TABLE XII", "Precision spraying efficiency and chemical savings comparison", "42"),
    ("TABLE XIII", "Navigation timing and mission motion execution profile", "42"),
    ("TABLE XIV", "Technical problems diagnosed during development and solutions applied", "43")
]

FIGURES_LIST = [
    ("Fig. 1", "Pioneer 3-DX differential kinematics and 3-DOF arm aiming geometry", "21"),
    ("Fig. 2", "EfficientNet-B0 deep neural network feature extractor architecture", "24"),
    ("Fig. 3", "Closed-loop proportional aisle guidance & heading control system block diagram", "28"),
    ("Fig. 4", "Complete end-to-end autonomous agricultural robot system architecture", "33"),
    ("Fig. 5", "Complete autonomous agricultural robot operational mission flowchart", "36"),
    ("Fig. 6", "End-effector inspection camera capture of the first plant canopy in Webots", "38"),
    ("Fig. 7", "Representative in-situ inspection frames annotated by EfficientNet-B0", "39"),
    ("Fig. 8", "EfficientNet-B0 model optimization curves over 25 epochs", "40"),
    ("Fig. 9", "Field inspection confusion matrix (66 leaves) and per-class performance metrics", "41"),
    ("Fig. 10", "Leaf-by-leaf AI inspection confidence across all 66 crop panels", "42"),
    ("Fig. 11", "Chemical volume and canopy treatment comparison (Targeted vs Broadcast)", "43"),
    ("Fig. 12", "Comprehensive AI agricultural robot testing field report dashboard", "44")
]

print("TOC and List mappings prepared")
