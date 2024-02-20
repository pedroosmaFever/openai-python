import time
import openai
import json

from openai.types.beta.threads.run import RequiredActionSubmitToolOutputs


def extract_and_print_fields(submit_tool_outputs: RequiredActionSubmitToolOutputs):

    tools_to_call = submit_tool_outputs.tool_calls
    tools_output_array: list = []

    for each_tool in tools_to_call:
        tool_call_id = each_tool.id
        function_name = each_tool.function.name
        function_args = each_tool.function.arguments

        # logging.info(f"Tool Call ID: {tool_call_id}, Function Name: {
        #              function_name}, Function Arguments: {function_args}")

        if function_name == "get_stock_price":
            break;
    


    # # Iterar sobre cada tool_call en submit_tool_outputs
    # for tool_call in submit_tool_outputs:
    #     print(tool_call)
    #     print(f"ID: {tool_call.id}")
    #     print(f"Function Name: {tool_call.function.name}")

    #     # Convertir el string de argumentos JSON en un diccionario
    #     arguments = json.loads(tool_call.function.arguments)
    #     for arg, value in arguments.items():
    #         print(f"{arg}: {value}")
    #     print("\n")  # Añade una línea en blanco para separar las salidas


# Imaginamos que ya tenemos configurado el cliente de OpenAI con la clave API
client = openai.OpenAI()

# Creación del asistente se mantiene igual
# assistant = client.beta.assistants.create(
#     name="Math Tutor",
#     instructions="You are a personal math tutor. Write and run code to answer math questions.",
#     tools=[{"type": "code_interpreter"}],
#     model="gpt-3.5-turbo",    
# )

# Creación del hilo se mantiene igual
thread = client.beta.threads.create()

# Ahora introducimos un bucle para preguntar continuamente al usuario
try:
    while True:
        # Solicitamos al usuario que introduzca un mensaje
        user_input = input("Enter your math question or type 'exit' to finish: ")
        if user_input.lower() == 'exit':
            break

        # Creación del mensaje con el input del usuario
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input,
        )

        # Creación de la ejecución se mantiene igual
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            #assistant_id=assistant.id,
            assistant_id="asst_pIoOSfsAwszdWrSEyBlbRhcj",
            #instructions="Please address the user as Jane Doe. The user has a premium account.",
        )

        print("Checking assistant status...")
        while True:
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

            if run.status == "completed":
                print("Done!")
                messages = client.beta.threads.messages.list(thread_id=thread.id)

                # Solo imprimimos el último mensaje
                if messages.data:  # Asegurar que hay al menos un mensaje
                    last_message = messages.data[0]  # Accedemos al último mensaje
                    # Suponiendo que la estructura de 'last_message.content' es la esperada y contiene texto
                    if last_message.content and len(last_message.content) > 0:
                        message_text = last_message.content[0].text.value
                    else:
                        message_text = "No message text found"
                    print(f"{last_message.role}: {message_text}")
                break
            elif run.status == "requires_action":
                print(f"requires_action... {run.required_action.type} {run.required_action.submit_tool_outputs.tool_calls}")
                extract_and_print_fields(run.required_action.submit_tool_outputs)
                #client.beta.threads.runs.submit_tool_outputs(thread_id=thread.id, run_id=run.id, )

            else:
                print(f"In progress... {run.status}")
                time.sleep(1)

finally:
    time.sleep(1)
    # Aseguramos que el asistente se elimine después de salir del bucle
    #client.beta.assistants.delete(assistant.id)
