import time
import openai
import json
import os
import requests

from openai.types.beta.threads.run import RequiredActionSubmitToolOutputs

import requests
import json
import os

def call_api_function(function_name, function_args_str):
    apiUrl = f"https://santagema-api-prod.azurewebsites.net/{function_name}"

    headers = {
        'Authorization': f'Bearer {os.environ.get("SGHUBDOCS_SECRETARY_KEY")}',
        'Content-Type': 'application/json'
    }

    try:
        if isinstance(function_args_str, str):
            function_args = json.loads(function_args_str)
        else:
            function_args = function_args_str

        tipo_peticion = function_args.pop('tipo_peticion', None)

#        if tipo_peticion not in ["POST", "GET"]:
#            return "Tipo de petición no soportado o ausente"

        if tipo_peticion == "POST":
            response = requests.post(apiUrl, json=function_args, headers=headers)
        else: #GET o sin especificar
            response = requests.get(apiUrl, params=function_args, headers=headers)

        if response.status_code >= 200 and response.status_code < 300:
            if 'application/json' in response.headers['Content-Type']:
                try:
                    return json.dumps(response.json())
                except json.JSONDecodeError:
                    return "Error al decodificar el JSON"
            else:
                return response.text
        else:
            return f"Error en la solicitud: {response.status_code}, Respuesta: {response.text}"
    except requests.ConnectionError:
        return "Error de conexión"
    except requests.Timeout:
        return "La solicitud ha superado el tiempo de espera"
    except requests.RequestException as e:
        return f"Error en la solicitud: {e}"



def submit_tool_outputs(thread_id, run_id, tools_to_call):
    tool_output_array = []
    for tool in tools_to_call:
        output = None
        tool_call_id = tool.id
        function_name = tool.function.name
        function_args = tool.function.arguments

        output = call_api_function(function_name, function_args)
        print(f"Tool Call ID: {tool_call_id}, Function Name: {function_name}, Function Arguments: {function_args} --> Output: {output}")
        #print(f" {function_name} -> {function_args} -> {output}")
        #print(f" {function_name} ")
        if output:
            tool_output_array.append({"tool_call_id": tool_call_id, "output": output})

    #compruebo si tool_output_array es vacío y devuelvo un no es posible ejecutar la solicitud y devuelve el tools_output_array en el mensaje de error
    if not tool_output_array:
        return f"No es posible ejecutar la solicitud"
    else:
        return client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=tool_output_array
    )


def extract_and_print_fields(submit_tool_outputs: RequiredActionSubmitToolOutputs):

    tools_to_call = submit_tool_outputs.tool_calls
    tools_output_array: list = []

    for each_tool in tools_to_call:
        tool_call_id = each_tool.id
        function_name = each_tool.function.name
        function_args = each_tool.function.arguments

        #print(f"Tool Call ID: {tool_call_id}, Function Name: {function_name}, Function Arguments: {function_args}")
        print(f"{function_name} -> {function_args}")

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
        #user_input = input("Enter your math question or type 'exit' to finish: ")
        user_input = input("User: ")
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

        #print("Checking assistant status...")
        while True:
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

            if run.status == "completed":
                print()
                #print("Done!")
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
                print("a", end="", flush=True)
                #print(f"requires_action... {run.required_action.type} {run.required_action.submit_tool_outputs.tool_calls}")
                #extract_and_print_fields(run.required_action.submit_tool_outputs)
                submit_tool_outputs(thread_id=thread.id, run_id=run.id, tools_to_call=run.required_action.submit_tool_outputs.tool_calls)
                #client.beta.threads.runs.submit_tool_outputs(thread_id=thread.id, run_id=run.id, )

            else:
                #print(f"In progress... {run.status}")
                print(".", end="", flush=True)
                time.sleep(1)

finally:
    time.sleep(1)
    # Aseguramos que el asistente se elimine después de salir del bucle
    #client.beta.assistants.delete(assistant.id)
