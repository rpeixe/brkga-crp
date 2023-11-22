import pandas as pd

class CrpInstance():
    """
    Represents an instance for the culture rotation problem.

    Matriz da forma
    28 linhas e 3 colunas

    posiçao 25-28 adubação verde
    cultura|familia|periodo de plantação
    """

    def __init__(self, filename: str):
        """
        Initializes the instance loading from a file.
        """
        nome = filename + '.csv'
        # Read the CSV file
        culturas_dados = pd.read_csv(nome)
        self.numero_lotes = 10
        self.duracao_plantio = 72
        self.cultura_verde = 4
        self.cultura_normal = 24
        self.matriz_dados = culturas_dados.values
        self.terrenos = [[-1] * self.duracao_plantio for _ in range(self.numero_lotes)]
        self.vetor_culturas_tam = 0
        self.posicao_cultura = []
        self.min_duracao = min([cultura[2] for cultura in self.matriz_dados])
        self.num_nodes = self.get_num_nodes()

    def get_num_nodes(self):
      soma=0
      for i in range(self.cultura_normal):
        soma += self.duracao_plantio//self.matriz_dados[i][2] * self.numero_lotes // 2
        self.posicao_cultura.append(soma)
      # soma *= self.numero_lotes//2
      self.vetor_culturas_tam=soma
      soma += 2*self.numero_lotes
      return soma
    
    def reset(self):
       for i in range(len(self.terrenos)):
          for j in range(len(self.terrenos[i])):
             self.terrenos[i][j] = -1