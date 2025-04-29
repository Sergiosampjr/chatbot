import time
import streamlit as st
from vanna_calls import (
    generate_questions_cached,
    generate_sql_cached,
    run_sql_cached,
    generate_plotly_code_cached,
    generate_plot_cached,
    generate_followup_cached,
    should_generate_chart_cached,
    is_sql_valid_cached,
    generate_summary_cached
)

avatar_url = "https://www.canva.com/design/DAGWkWkNv4w/5EGL2tsZ5_mV_ZiZTwS0pQ/view?utm_content=DAGWkWkNv4w&utm_campaign=designshare&utm_medium=link&utm_source=editor"



st.set_page_config(layout = "wide")


st.sidebar.title("Configurações")
st.sidebar.checkbox("Mostrar SQL", value = True, key = "Mostrar_sql")
st.sidebar.checkbox("Mostrar tabela", value = True, key = "show_table")
st.sidebar.checkbox("Mostrar código de plotagem", value = True,key = "mostar_codigo_de_plotagem")
st.sidebar.checkbox("Mostrar Gráfico", value = True,key = "Mostrar_Gráfico")
st.sidebar.checkbox("Mostrar resumo", value = True,key = "Mostrar_resumo")
st.sidebar.checkbox("Mostrar perguntas de acompanhamento",value = True,key = "mostrar_acompanhamento")
#repor = st.sidebar.checkbox("Repor")



st.title("Assistente de Dennis")


def definir_pergunta(pergunta):
    st.session_state["Minha pergunta"] = pergunta


mensagem_do_assistente_sugerida = st.chat_message("assistant", avatar = avatar_url)

if mensagem_do_assistente_sugerida.button("Clique para mostrar sugestões de perguntas"):
    st.session_state["Minha pergunta"] = None
    perguntas = generate_questions_cached()
    for i ,pergunta in enumerate(perguntas):
        time.sleep(0.05)
        botao = st.button(
        pergunta,
        on_click = definir_pergunta,
        args = (pergunta,),
        )


minha_pergunta = st.session_state.get("Minha pergunta",default = None)


if minha_pergunta is None:
    minha_pergunta = st.chat_input(
        "Faça-me uma pergunta sobre os seus dados"
    )

if minha_pergunta:
    st.session_state["Minha pergunta"] = minha_pergunta
    usuario_mensagem = st.chat_message("Usuário")
    usuario_mensagem.write(f"{minha_pergunta}")

    sql = generate_sql_cached(question = minha_pergunta)

    if sql:
        if is_sql_valid_cached(sql = sql):
            if st.session_state.get("Mostrar sql",True):
                assistente_mensagem_sql = st.chat_message(
                    "assistant", avatar = avatar_url
                )
                assistente_mensagem_sql.code(sql, language = "sql", line_numbers = True)
        else:
            assistente_mensagem = st.chat_message(
                "Assistant",avatar = avatar_url
            )        
            assistente_mensagem.write(sql)
            st.stop()

        df = run_sql_cached(sql = sql)

        if df is not None:
            st.session_state["df"] = df

        if st.session_state.get("df") is not None:
            if st.session_state.get("Mostrar tabela", True):
                df = st.session_state.get("df")
                assistante_mensagem_tabela = st.chat_message(
                    "Assistant",
                    avatar = avatar_url,


                )           
                if len(df) > 10:
                    assistante_mensagem_tabela.text("Primeiras 10 linhas dos dados")
                    assistante_mensagem_tabela.dataframe(df.head(10))
                else:
                    assistante_mensagem_tabela.dataframe(df)
            
            if should_generate_chart_cached(question = minha_pergunta,sql = sql,df = df):

                code = generate_plotly_code_cached(question = minha_pergunta,sql = sql,df = df)

                if st.session_state.get("Mostrar código de plotagem", False):
                    codigo_plotagem_mensagem_cliente = st.chat_message(
                        "assistant",       
                        avatar = avatar_url
                    )          
                    codigo_plotagem_mensagem_cliente.code(
                        code, language = "python", line_numbers = True
                    )                
                if code is not None and code != "":
                    if st.session_state.get("Mostrar gráfico", True):
                        assistante_mensagem_grafico = st.chat_message(
                            "Assistant",
                            avatar = avatar_url
                        )
                        fig = generate_plot_cached(code = code,df = df)
                        if fig is not None:
                            assistante_mensagem_grafico.plotly_chart(fig)
                        else:
                            assistante_mensagem_grafico.error("Não consegui gerar um gráfico")


            if st.session_state.get("Mostrar resumo", True):
                assistante_mensagem_resumo = st.chat_message(
                    "Assistant",
                    avatar = avatar_url        
                )                   
                resumo = generate_summary_cached(question = minha_pergunta, df = df)
                if resumo is not None:
                    assistante_mensagem_resumo.text(resumo)


            if st.session_state.get("Mostrar acompanhamento", True):
                assistante_mensagem_acompanhamento = st.chat_message(
                    "assistant",
                    avatar = avatar_url
                )    
                acompanhamento_perguntas = generate_followup_cached(
                    question = minha_pergunta,sql = sql,df = df        

                )
                st.session_state["df"] = None

                if len(acompanhamento_perguntas) > 0:
                    assistante_mensagem_acompanhamento.text(
                        "Aqui estão algumas possíveis perguntas de acompanhamento"        

                    )
                    #Imprima as 5 primeiras perguntas de acompanhamento
                    for pergunta in acompanhamento_perguntas[:5]:
                        assistante_mensagem_acompanhamento.button(pergunta, on_click = definir_pergunta, args=(pergunta,))  


    else:
        assistante_mensagem_erro = st.chat_message(
            "assistant", avatar=avatar_url
        )
        assistante_mensagem_erro.error("Não consegui gerar SQL para essa pergunta")





