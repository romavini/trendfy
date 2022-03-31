import glob


class Model:
    def __init__(self):
        pass

    def recursive_rev(self, current_rev, list_revs):
            for num, rev in enumerate(list_revs):
                self.revx(current, rev, num)

    def revx(self, rev_current, rev, num):

        if (rev - rev_current) > 1 or num > 0:

        # Write from mean previvaz weeks out
        text_files = glob.glob("input/previvaz_out/*.DAT", recursive=True)
        text_files.sort(key=self.sortKeyFunc)

        text = ''

        predictors = self.read_predictors()
        for nline, file in enumerate(text_files, start=1):
            with open(file, encoding="ISO-8859-1") as currentFile:
                previvaz_text = currentFile.readlines()

            previvaz_text = currentFile.readlines()

            means = [round(float(previvaz_text[1][25:33].strip())),
                     round(float(previvaz_text[1][34:42].strip())),
                     round(float(previvaz_text[1][43:51].strip())),
                     round(float(previvaz_text[1][52:60].strip())),
                     round(float(previvaz_text[1][61:69].strip())),
                     round(float(previvaz_text[1][70:78].strip()))]

            if predictors.loc[predictors.cod_posto == int(previvaz_text[1][5:9]),
                        ['tipo_preditor']].values[0][0] in ['Agente', 'Calculado',
                                               'Regressão Diária', 'Estimado*']:
                text += str(nline).rjust(6)
                text += cod_posto.rjust(5)

                # if cod_posto == line[8:11].strip():

                for j, mean in enumerate(means):
                    text += str(mean).rjust(10)

                text += '\n'

            elif predictors.loc[predictors.cod_posto == int(previvaz_text[1][5:9]),
                        ['tipo_preditor']].values[0][0] in ['SMAP', 'CPINS']:

                text += str(nline).rjust(6)
                text += cod_posto.rjust(5)

                # Write from mean SMAP weeks
                df = pd.read_csv(self.mean_chuva_vazao)
                weeks = df.loc[df['Código Posto'] == int(previvaz_text[1][5:9])].iloc[0, -3-rev:-1]

                for week in weeks:
                    text += str(int(float(week))).rjust(10)


                for j, mean in enumerate(means[:4-rev]):
                    text += str(mean).rjust(10)
                text += '\n'

            else:
                print('\n')
                print("ERROR IN PREVS MOUNTING!")
                print('Post:', previvaz_text[1][5:9])
                print('\n')

        with open(f"output/0/Prevs_VE_202201.rv{rev}", 'w') as f:
            f.writelines(text)

        revisao = f'rv{rev}'
        #self.update_prevs(revisao)

        return True

if __name__ == '__main__':
    model = Model()
    model.recursive_rev()
