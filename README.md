SNA2014_Homework3
=================

The programs to develop and evaluate the homework 3 in the course "Social Network Analysis" (SNA), National Taiwan University, 2014 fall

### Homework 3

Students are allowed to ask the query system for the neighbors of a given node, and try to unbiasedly sample a large social network using the query process.

Initially, students can access a sampled subgraph as the seed of the social network.

### Used Datasets

- [Pokec network at SNAP](http://snap.stanford.edu/data/soc-pokec.html)
- [Catster/Dogster familylinks/friendship](http://konect.uni-koblenz.de/networks/petster-carnivore)

### Environment

- PHP for .php files
- C 99 for .c files
- Python 3 with library NetworkX for .py files

### File descriptions

- *distribution_computation.py*: To compute the distributions of degree and attributes of a social network.
- *kl_divergence_computation.py*: To compute the symmetric KL divergence of given two probability distributions.
- *homework_difficulty_test.py*: To test the strength of the baseline solution (always selecting the node with max degree).
- *homework_connection_test.py*: To test the connnection quality of the query system.
- *php_query_connection.py (query.py)*: to connect to the query system and obtain information in response to the query.
- *query_system.php*: The main query system for this homework. The system accesses the database storing social networks.
- *seed_subgraph_generation.php*: To generate a sampled subgraph as the seed.
- *node_id_encoding.php (node_convertion.php)*: To encode a node integer ID by prime multiplicative inverse.
- *graph_closeness_centrality.c*: To fast compute the closeness centrality of every node in a social network. The program is the combination of graph adjacency list and BFS.
- *team_password_generation.c*: To generate a specific password for each team to access the query system. 
- *petster_data_preprocessing.py*: To extract useful features from the original catster/dogster network.
- *submission_file_format_verification.py*: To verify the integrity of the file formats from students.
- *result_comparison_with_answers.py*: The compare a student's homework answers and TA's standard answers.
