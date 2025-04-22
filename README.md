# Generating Guitar Solos by Integer Programming 🎸

This project contains code related to the paper:

**"Generating guitar solos by integer programming"**  
Nailson dos Santos Cunha, Anand Subramanian, and Dorien Herremans  
*Journal of the Operational Research Society*, 69(6), 971–985  
[https://doi.org/10.1080/01605682.2017.1390528](https://doi.org/10.1080/01605682.2017.1390528)

---

## Abstract

In this paper, we present a framework for computer-aided composition (CAC) that uses exact combinatorial optimisation methods to generate guitar solos from a newly proposed data-set of licks over an accompaniment based on the 12-bar blues chord progression. An integer programming formulation, which can be solved to optimality by a branch-and-cut algorithm, was developed for this problem whose objective is to determine an optimal sequence of a set of licks given a matrix of transition costs derived from user preferences. The generated solos are displayed in tablature format. Outputs of the system were evaluated in an empirical experiment with 173 participants. The results show that the solos whose licks were optimally sequenced were significantly more enjoyed than those randomly sequenced. We project that the developed framework could be of potential use to guitarists looking for original material; as an educational tool for future composers; and to support composers in discovering unique and novel compositional ideas.

---

👉 You can find **examples of generated guitar solos** here:  
[https://dorienherremans.com/guitarsolos](https://dorienherremans.com/guitarsolos)

---

## Citation

If you use this code or the ideas from the paper, please cite:

```bibtex
@article{Cunha03062018,
  author = {Nailson dos Santos Cunha and Anand Subramanian and Dorien Herremans and},
  title = {Generating guitar solos by integer programming},
  journal = {Journal of the Operational Research Society},
  volume = {69},
  number = {6},
  pages = {971--985},
  year = {2018},
  publisher = {Taylor \& Francis},
  doi = {10.1080/01605682.2017.1390528},
  URL = {
          https://doi.org/10.1080/01605682.2017.1390528
  },
  eprint = {
          https://doi.org/10.1080/01605682.2017.1390528
  }
}
```

---

NOTE: It is necessary to create an "obj" folder inside the project folder.
