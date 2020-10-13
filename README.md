# ConTraSim: Generating Contextual Trajectories from User Profiles

Jian Yang, Christian Poellabauer, Pramita Mitra, Abhishek Sharma, CynthiaNeubecker, and Arpita Chand.

This repository contains codes to the implementation of the paper "Generating Contextual Trajectories from User Profiles" accepted by 3rd ACM SIGSPATIAL International Workshop onGeoSpatial Simulation (GeoSim’20). 


## Abstract 
The trajectory of traffic participants is an essential source for pattern mining and knowledge discovery in urban mobility. However, real-world trajectory data are often not publicly available due to privacy concerns or intellectual property constraints. Although some simulators or synthetic trajectory datasets have been proposed, many of them only consider the spatial-temporal aspects of the trajectory data, but ignore other contextual information that could impact trajectories. On one hand, trajectories are usually associated with and affected by user profiles (e.g., a person's daily routines and preferred modes of transportation). On the other hand, an individual's movements are also affected by environmental conditions and interactions with other traffic participants, particularly in urban scenarios (e.g., routing choices due to congestion or road conditions). Such contextual trajectories provide a more realistic representation of the mobility patterns of traffic participants. Due to the lack of such datasets or trace generators, this work presents ConTraSim (Contextual Trajectory Simulation), a novel approach for generating contextual trajectories based on the Simulation of Urban MObility (SUMO) traffic simulator. More specifically, the proposed approach is designed to produce GPS traces annotated by contextual information that mimic the movements of multiple types of traffic participants in urban areas. As a case study, we also generate a sample dataset using the proposed method and compare it to real-world data to demonstrate how well the synthetic data reflects real-world data characteristics.


## Dependencies
This project was developed and tested with the following dependencies
- Python 3.7
- sumolib (SUMO version 1.6.0 for Linux)
- pandas 1.1.0


## Data Source
For survey-based profile modeling, an anoymized sample user profile is provided under the path '/data/profiles'. 
For sample-based profile modeling, the GeoLife dataset is used and can be download [here](https://www.microsoft.com/en-us/download/details.aspx?id=52367).


## Citation
If you find the code useful, please cite our paper：
```
@inproceedings{yang2020generating,
  title={Generating Contextual Trajectories from User Profiles},
  author={Yang, Jian and Poellabauer, Christian and Mitra, Pramita and Sharma, Abhishek and Neubecker, Cynthia and Chand, Arpita},
  booktitle={3rd ACM SIGSPATIAL International Workshop on GeoSpatial Simulation (GeoSim’20)},
  year={2020},
  organization={ACM}
}
```
