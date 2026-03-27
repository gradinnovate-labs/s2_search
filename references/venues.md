# Venue Name Expansion Reference

Semantic Scholar recognizes various venue name formats. Use this reference to expand abbreviations to include common variations.

## Conference Abbreviations

### Machine Learning

| Abbreviation | Full Name | Also Known As |
|--------------|-----------|---------------|
| NeurIPS | Neural Information Processing Systems | Conference on Neural Information Processing Systems, NIPS |
| ICML | International Conference on Machine Learning | |
| ICLR | International Conference on Learning Representations | |

### Natural Language Processing

| Abbreviation | Full Name | Also Known As |
|--------------|-----------|---------------|
| ACL | Annual Meeting of the Association for Computational Linguistics | Association for Computational Linguistics |
| EMNLP | Conference on Empirical Methods in Natural Language Processing | Empirical Methods in Natural Language Processing |
| NAACL | North American Chapter of the Association for Computational Linguistics | North American Association for Computational Linguistics |
| COLING | International Conference on Computational Linguistics | |

### Computer Vision

| Abbreviation | Full Name | Also Known As |
|--------------|-----------|---------------|
| CVPR | Computer Vision and Pattern Recognition | Conference on Computer Vision and Pattern Recognition |
| ICCV | IEEE International Conference on Computer Vision | International Conference on Computer Vision |

### General AI

| Abbreviation | Full Name | Also Known As |
|--------------|-----------|---------------|
| AAAI | AAAI Conference on Artificial Intelligence | Association for the Advancement of Artificial Intelligence |
| IJCAI | International Joint Conference on Artificial Intelligence | |

### Data & Web

| Abbreviation | Full Name | Also Known As |
|--------------|-----------|---------------|
| KDD | Knowledge Discovery and Data Mining | ACM SIGKDD Conference on Knowledge Discovery and Data Mining |
| WWW | The Web Conference | World Wide Web Conference, International World Wide Web Conference |
| SIGIR | Annual International ACM SIGIR Conference on Research and Development in Information Retrieval | |

### Robotics

| Abbreviation | Full Name | Also Known As |
|--------------|-----------|---------------|
| ICRA | IEEE International Conference on Robotics and Automation | International Conference on Robotics and Automation |

### Databases & Systems

| Abbreviation | Full Name | Also Known As |
|--------------|-----------|---------------|
| SIGMOD | ACM SIGMOD International Conference on Management of Data | Management of Data |
| VLDB | Very Large Data Bases | |

### Graphics

| Abbreviation | Full Name | Also Known As |
|--------------|-----------|---------------|
| SIGGRAPH | ACM SIGGRAPH Conference | Special Interest Group on Computer Graphics |

### VLSI & EDA

| Abbreviation | Full Name | Also Known As |
|--------------|-----------|---------------|
| DAC | Design Automation Conference | ACM/IEEE Design Automation Conference |
| ICCAD | International Conference on Computer Aided Design | IEEE/ACM International Conference on Computer-Aided Design |
| ISPD | ACM International Symposium on Physical Design | International Symposium on Physical Design |
| ASP-DAC | Asia and South Pacific Design Automation Conference | |
| DATE | Design, Automation and Test in Europe | |
| FPGA Symposium | Symposium on Field Programmable Gate Arrays | ACM/SIGDA International Symposium on Field Programmable Gate Arrays |
| VLSI Design | International Conference on VLSI Design | IEEE International Conference on VLSI Design |
| CAV | International Conference on Computer Aided Verification | Computer Aided Verification |
| ITC | International Test Conference | IEEE International Test Conference |
| CICC | IEEE Custom Integrated Circuits Conference | Custom Integrated Circuits Conference |
| SLIP | International Workshop on System-Level Interconnect Prediction | System Level Interconnect Prediction |

## Journal Abbreviations

### Top Science Journals

| Abbreviation | Full Name | Also Known As |
|--------------|-----------|---------------|
| Nature | Nature | |
| Science | Science | |
| Cell | Cell | |
| PNAS | Proceedings of the National Academy of Sciences of the United States of America | Proceedings of the National Academy of Sciences |

### EDA & Hardware

| Abbreviation | Full Name | Also Known As |
|--------------|-----------|---------------|
| TCAD | IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems | IEEE TCAD |
| TODAES | ACM Transactions on Design Automation of Electronic Systems | ACM Trans. Design Autom. Electr. Syst. |

### Computer Systems

| Abbreviation | Full Name | Also Known As |
|--------------|-----------|---------------|
| ACM TOCS | ACM Transactions on Computer Systems | Transactions on Computer Systems |
| IEEE TPDS | IEEE Transactions on Parallel and Distributed Systems | |

### Software & AI

| Abbreviation | Full Name | Also Known As |
|--------------|-----------|---------------|
| IEEE TSE | IEEE Transactions on Software Engineering | |
| IEEE TPAMI | IEEE Transactions on Pattern Analysis and Machine Intelligence | |
| IEEE TNNLS | IEEE Transactions on Neural Networks and Learning Systems | |
| JMLR | Journal of Machine Learning Research | Journal of machine learning research |

### ACM Transactions

| Abbreviation | Full Name | Also Known As |
|--------------|-----------|---------------|
| TODS | ACM Transactions on Database Systems | |
| TOIS | ACM Transactions on Information Systems | |
| Computing Surveys | ACM Computing Surveys | |
| JACM | Journal of the ACM | |

## Expansion Examples

### Example 1: ACL

```json
// User says: "Find papers from ACL"
// Expand to:
{
  "venue": [
    "ACL",
    "Annual Meeting of the Association for Computational Linguistics",
    "Association for Computational Linguistics"
  ]
}
```

### Example 2: TODAES

```json
// User says: "Search TODAES"
// Expand to:
{
  "venue": [
    "TODAES",
    "ACM Transactions on Design Automation of Electronic Systems",
    "ACM Trans. Design Autom. Electr. Syst.",
    "Transactions on Design Automation of Electronic Systems"
  ]
}
```

## Tips

1. **Include multiple variations**: Semantic Scholar may index venues under different names
2. **Use abbreviated forms for journals**: Some journals like TODAES work better with abbreviated forms
3. **Check case sensitivity**: JMLR prefers lowercase "Journal of machine learning research"
4. **Combine with publicationTypes**: Use `"publicationTypes": ["Conference"]` or `["JournalArticle"]` for better filtering
