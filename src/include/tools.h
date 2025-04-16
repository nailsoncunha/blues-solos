#ifndef TOOLS_H
#define TOOLS_H


# include <ilcplex/ilocplex.h>

//#define LI 25
//#define NC 12


/*
 * Recebe um array de inteiros que é a matriz de penalidades
 * e retorna a matriz preenchida. 
 */
int matriz_penalidades(double** matriz, int instancia);


/*
 * Recebe um array de inteiros e lê de um arquivo a qntd de
 * compassos de cada lick. Preenche o array com o compassos dos licks.
 */
int compassos_licks(int compassos[], int instancia);


/*
* Recebe um array de inteiros, lê o arquivo cindex e preenche
* o array com os indices equivalentes a licks coringa
*
*/
int coringa_index(int cindexes[]);



/*
* Recebe um array de inteiros, lê o arquivo taindex e preenche
* o array com os indices equivalentes a licks turnaround
*
*/
int turnaround_index(int taindexes[]);



/*
* Recebe um array de inteiros, lê o arquivo rindex e preenche
* o array com os indices equivalentes a licks com pausa no comeco ou no fim
*
*/
int rest_index(int rindexes[]);


/*
* Recebe um array de inteiros, lê o arquivo prindex e preenche
* o array com os indices equivalentes a licks que estão proibidos de serem utilizados
*
*/
int prohibited_index(int prindexes[]);

#endif
