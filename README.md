# 📊 RFV – Segmentação de Clientes com Streamlit

Aplicação web desenvolvida em **Python + Streamlit** para segmentação de clientes utilizando a metodologia **RFV (Recência, Frequência e Valor)**.  
O objetivo é permitir que qualquer pessoa suba uma base de compras e obtenha, de forma automática, **classificação de clientes e ações de marketing sugeridas**.

---

## 🚀 Funcionalidades

- Upload de arquivos `.csv` ou `.xlsx`
- Cálculo automático de:
  - **Recência (R)** – dias desde a última compra
  - **Frequência (F)** – número de compras
  - **Valor (V)** – total gasto
- Segmentação por **quartis (A, B, C, D)**
- Geração do **RFV Score** (ex: AAA, BCA, DDD)
- Sugestão de **ações de marketing/CRM**
- Download do resultado final em **Excel**
- Interface web simples e intuitiva

---

## 🧠 O que é RFV?

RFV é uma técnica de segmentação de clientes baseada em comportamento de compra:

- **Recência (R):** quanto menor, melhor
- **Frequência (F):** quanto maior, melhor
- **Valor (V):** quanto maior, melhor

Cada métrica é classificada em quartis:
- **A** → melhor grupo  
- **D** → pior grupo  

Exemplo de score:
- `AAA` → clientes mais valiosos
- `DDD` → clientes com alto risco de churn

---

## 🛠️ Tecnologias Utilizadas

- Python 3.10+
- Streamlit
- Pandas
- NumPy
- OpenPyXL
- XlsxWriter

---

## 📂 Estrutura do Projeto

```text
rfv-project/
│
├── app_RFV.py        # Aplicação Streamlit
├── requirements.txt  # Dependências do projeto
├── .gitignore
└── README.md
```
# 📊 Projeto RFV (Recência, Frequência e Valor)

Este projeto realiza a segmentação de clientes utilizando a metodologia RFV, ajudando a identificar os melhores clientes e estratégias de marketing.

## ▶️ Executar Localmente

### 1️⃣ Clonar o repositório
```bash
git clone https://github.com/RennanRnz/rfv-project.git
cd rfv-project
```
### 2️⃣ Criar e ativar ambiente virtual

**Windows (Git Bash / PowerShell):**
```bash
python -m venv venv
source venv/Scripts/activate
```
### Instalar dependências

```bash
pip install -r requirements.txt
```
### 4️⃣ Executar a aplicação

```bash
streamlit run app_RFV.py
```
## 🌐 Deploy

A aplicação está preparada para deploy no **Render**, utilizando:

*   **Build Command:** `pip install -r requirements.txt`
*   **Start Command:** `streamlit run app_RFV.py --server.port $PORT --server.address 0.0.0.0`

## 📈 Exemplo de Uso

Suba um arquivo contendo as seguintes colunas:
*   `ID_cliente`
*   `CodigoCompra`
*   `DiaCompra`
*   `ValorTotal`

**Funcionalidades:**
*   A aplicação calcula o RFV automaticamente.
*   Visualize os segmentos de clientes.
*   Baixe o resultado processado em Excel.

## 👤 Autor

**Rennan Silva**
*Data Scientist*

🔗 [GitHub](https://github.com/RennanRnz))

## ⭐ Considerações Finais

Este projeto pode ser facilmente adaptado para:
*   CRM
*   E-commerce
*   Marketing digital
*   Retenção e fidelização de clientes

Sinta-se à vontade para clonar, adaptar e evoluir 🚀

