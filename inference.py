import openai
import time, tiktoken
from openai import OpenAI
import os, anthropic, json
import google.generativeai as genai

TOKENS_IN = dict()
TOKENS_OUT = dict()

# 默认使用 ohmygpt 作为 OpenAI 兼容网关
# 如需切换到官方 OpenAI，可设置环境变量 OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_COMPAT_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.ohmygpt.com/v1")

encoding = tiktoken.get_encoding("cl100k_base")

def curr_cost_est():
    costmap_in = {
        "gpt-4o": 2.50 / 1000000,
        "gpt-4o-mini": 0.150 / 1000000,
        "gpt-5.4-mini": 0.160 / 1000000,
        "o1-preview": 15.00 / 1000000,
        "o1-mini": 3.00 / 1000000,
        "claude-3-5-sonnet": 3.00 / 1000000,
        "deepseek-chat": 1.00 / 1000000,
        "gemini-3-flash-preview": 0.00 / 1000000,  # 占位成本，按需调整
        "o1": 15.00 / 1000000,
        "o3-mini": 1.10 / 1000000,
    }
    costmap_out = {
        "gpt-4o": 10.00/ 1000000,
        "gpt-4o-mini": 0.6 / 1000000,
        "gpt-5.4-mini": 0.60 / 1000000,
        "o1-preview": 60.00 / 1000000,
        "o1-mini": 12.00 / 1000000,
        "claude-3-5-sonnet": 12.00 / 1000000,
        "deepseek-chat": 5.00 / 1000000,
        "gemini-3-flash-preview": 0.00 / 1000000,  # 占位成本，按需调整
        "o1": 60.00 / 1000000,
        "o3-mini": 4.40 / 1000000,
    }
    return sum([costmap_in[_]*TOKENS_IN[_] for _ in TOKENS_IN]) + sum([costmap_out[_]*TOKENS_OUT[_] for _ in TOKENS_OUT])

def query_model(model_str, prompt, system_prompt, openai_api_key=None, gemini_api_key=None,  anthropic_api_key=None, siliconflow_api_key=None, tries=5, timeout=5.0, temp=None, print_cost=True, version="1.5"):
    """
    统一的模型调用入口。
    说明：
    - 不再真实使用 siliconflow_api_key，而是通过 ohmygpt（OpenAI 兼容网关）访问。
    - 为了兼容旧代码，保留 siliconflow_api_key 参数，但会忽略其值。
    - 若 ``fashion_config.yaml`` → ``local-llm.enabled`` 且 ``llm-backend`` 指向本地模型，则走 vLLM 等本地 OpenAI 兼容端点。
    """
    try:
        from plugins.local_llm import try_local_chat_completion

        local_answer = try_local_chat_completion(
            model_str=model_str,
            system_prompt=system_prompt,
            user_prompt=prompt,
            temperature=temp,
        )
        if local_answer is not None:
            if print_cost:
                print("[local-llm] generation via local OpenAI-compatible endpoint")
            return local_answer
    except Exception as e:
        print(f"[local-llm] fallback to remote API: {e}")

    preloaded_api = os.getenv('OPENAI_API_KEY')
    if openai_api_key is None and preloaded_api is not None:
        openai_api_key = preloaded_api
    # 兼容旧逻辑：如果没有显式 openai_api_key，但设置了 OHMYGPT_API_KEY，则优先使用
    if openai_api_key is None and os.getenv("OHMYGPT_API_KEY"):
        openai_api_key = os.getenv("OHMYGPT_API_KEY")

    if openai_api_key is None and anthropic_api_key is None:
        raise Exception("No API key provided in query_model function")
    if openai_api_key is not None:
        openai.api_key = openai_api_key
        os.environ["OPENAI_API_KEY"] = openai_api_key
    if anthropic_api_key is not None:
        os.environ["ANTHROPIC_API_KEY"] = anthropic_api_key
    if gemini_api_key is not None:
        os.environ["GEMINI_API_KEY"] = gemini_api_key
    for _ in range(tries):
        try:
            # 标准化模型字符串（去除首尾空格）
            model_str = model_str.strip() if model_str else model_str
            # 调试输出：查看实际使用的模型字符串
            if _ == 0:
                print(f"[DEBUG] Querying model: '{model_str}'")
            # 兼容旧配置：如果仍然使用 siliconflow-deepseek-v3.2 / deepseek-v3.2 名称，
            # 统一映射到 gpt-4o，通过 ohmygpt 网关调用
            if model_str in ["siliconflow-deepseek-v3.2", "deepseek-v3.2"]:
                model_str = "gpt-4o"

            if model_str == "gpt-4o-mini" or model_str == "gpt4omini" or model_str == "gpt-4omini" or model_str == "gpt4o-mini":
                model_str = "gpt-4o-mini"
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}]
                if version == "0.28":
                    if temp is None:
                        completion = openai.ChatCompletion.create(
                            model=f"{model_str}",  # engine = "deployment_name".
                            messages=messages
                        )
                    else:
                        completion = openai.ChatCompletion.create(
                            model=f"{model_str}",  # engine = "deployment_name".
                            messages=messages, temperature=temp
                        )
                else:
                    client = OpenAI(base_url=OPENAI_COMPAT_BASE_URL, api_key=openai_api_key)
                    if temp is None:
                        completion = client.chat.completions.create(
                            model="gpt-4o-mini-2024-07-18", messages=messages, )
                    else:
                        completion = client.chat.completions.create(
                            model="gpt-4o-mini-2024-07-18", messages=messages, temperature=temp)
                answer = completion.choices[0].message.content

            elif model_str == "gemini-3-flash-preview":
                # 通过 ohmygpt 的 OpenAI 兼容接口调用 gemini-3-flash-preview
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
                client = OpenAI(base_url=OPENAI_COMPAT_BASE_URL, api_key=openai_api_key)
                if temp is None:
                    completion = client.chat.completions.create(
                        model="gemini-3-flash-preview", messages=messages
                    )
                else:
                    completion = client.chat.completions.create(
                        model="gemini-3-flash-preview", messages=messages, temperature=temp
                    )
                answer = completion.choices[0].message.content

            elif model_str == "gpt-5.4-mini":
                # 通过 ohmygpt 的 OpenAI 兼容接口调用 gpt-5.4-mini
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
                client = OpenAI(base_url=OPENAI_COMPAT_BASE_URL, api_key=openai_api_key)
                if temp is None:
                    completion = client.chat.completions.create(
                        model="gpt-5.4-mini", messages=messages
                    )
                else:
                    completion = client.chat.completions.create(
                        model="gpt-5.4-mini", messages=messages, temperature=temp
                    )
                answer = completion.choices[0].message.content

            elif model_str == "gemini-2.0-pro":
                if gemini_api_key is None:
                    raise Exception("Gemini API key is required for gemini-2.0-pro model. Please provide gemini_api_key parameter or set GEMINI_API_KEY environment variable.")
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel(model_name="gemini-2.0-pro-exp-02-05", system_instruction=system_prompt)
                answer = model.generate_content(prompt).text
            elif model_str == "gemini-1.5-pro":
                if gemini_api_key is None:
                    raise Exception("Gemini API key is required for gemini-1.5-pro model. Please provide gemini_api_key parameter or set GEMINI_API_KEY environment variable.")
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel(model_name="gemini-1.5-pro", system_instruction=system_prompt)
                answer = model.generate_content(prompt).text
            elif model_str == "o3-mini":
                model_str = "o3-mini"
                messages = [
                    {"role": "user", "content": system_prompt + prompt}]
                if version == "0.28":
                    completion = openai.ChatCompletion.create(
                        model=f"{model_str}",  messages=messages)
                else:
                    client = OpenAI(base_url=OPENAI_COMPAT_BASE_URL, api_key=openai_api_key)
                    completion = client.chat.completions.create(
                        model="o3-mini-2025-01-31", messages=messages)
                answer = completion.choices[0].message.content

            elif model_str == "claude-3.5-sonnet":
                client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
                message = client.messages.create(
                    model="claude-3-5-sonnet-latest",
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}])
                answer = json.loads(message.to_json())["content"][0]["text"]
            elif model_str == "gpt4o" or model_str == "gpt-4o":
                model_str = "gpt-4o"
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}]
                if version == "0.28":
                    if temp is None:
                        completion = openai.ChatCompletion.create(
                            model=f"{model_str}",  # engine = "deployment_name".
                            messages=messages
                        )
                    else:
                        completion = openai.ChatCompletion.create(
                            model=f"{model_str}",  # engine = "deployment_name".
                            messages=messages, temperature=temp)
                else:
                    client = OpenAI(base_url=OPENAI_COMPAT_BASE_URL, api_key=openai_api_key)
                    if temp is None:
                        completion = client.chat.completions.create(
                            model="gpt-4o-2024-08-06", messages=messages, )
                    else:
                        completion = client.chat.completions.create(
                            model="gpt-4o-2024-08-06", messages=messages, temperature=temp)
                answer = completion.choices[0].message.content
            elif model_str == "deepseek-chat":
                model_str = "deepseek-chat"
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}]
                if version == "0.28":
                    raise Exception("Please upgrade your OpenAI version to use DeepSeek client")
                else:
                    deepseek_client = OpenAI(
                        api_key=os.getenv('DEEPSEEK_API_KEY'),
                        base_url="https://api.deepseek.com/v1"
                    )
                    if temp is None:
                        completion = deepseek_client.chat.completions.create(
                            model="deepseek-chat",
                            messages=messages)
                    else:
                        completion = deepseek_client.chat.completions.create(
                            model="deepseek-chat",
                            messages=messages,
                            temperature=temp)
                answer = completion.choices[0].message.content
            elif model_str == "o1-mini":
                model_str = "o1-mini"
                messages = [
                    {"role": "user", "content": system_prompt + prompt}]
                if version == "0.28":
                    completion = openai.ChatCompletion.create(
                        model=f"{model_str}",  # engine = "deployment_name".
                        messages=messages)
                else:
                    client = OpenAI(base_url=OPENAI_COMPAT_BASE_URL, api_key=openai_api_key)
                    completion = client.chat.completions.create(
                        model="o1-mini-2024-09-12", messages=messages)
                answer = completion.choices[0].message.content
            elif model_str == "o1":
                model_str = "o1"
                messages = [
                    {"role": "user", "content": system_prompt + prompt}]
                if version == "0.28":
                    completion = openai.ChatCompletion.create(
                        model="o1-2024-12-17",  # engine = "deployment_name".
                        messages=messages)
                else:
                    client = OpenAI(base_url=OPENAI_COMPAT_BASE_URL, api_key=openai_api_key)
                    completion = client.chat.completions.create(
                        model="o1-2024-12-17", messages=messages)
                answer = completion.choices[0].message.content
            elif model_str == "o1-preview":
                model_str = "o1-preview"
                messages = [
                    {"role": "user", "content": system_prompt + prompt}]
                if version == "0.28":
                    completion = openai.ChatCompletion.create(
                        model=f"{model_str}",  # engine = "deployment_name".
                        messages=messages)
                else:
                    client = OpenAI()
                    completion = client.chat.completions.create(
                        model="o1-preview", messages=messages)
                answer = completion.choices[0].message.content
            else:
                # 如果模型字符串不匹配任何已知模型，抛出异常
                raise Exception(
                    f"Unsupported or unrecognized model: '{model_str}'. Supported models: "
                    f"gpt-4o-mini, gpt-4o, deepseek-chat, o1-mini, o1, o1-preview, o3-mini, "
                    f"claude-3.5-sonnet, gemini-3-flash-preview, gemini-1.5-pro, gemini-2.0-pro"
                )

            try:
                if model_str in ["o1-preview", "o1-mini", "claude-3.5-sonnet", "o1", "o3-mini", "gemini-3-flash-preview"]:
                    encoding = tiktoken.encoding_for_model("gpt-4o")
                elif model_str in ["deepseek-chat", "siliconflow-deepseek-v3.2"]:
                    encoding = tiktoken.encoding_for_model("cl100k_base")
                else:
                    encoding = tiktoken.encoding_for_model(model_str)
                if model_str not in TOKENS_IN:
                    TOKENS_IN[model_str] = 0
                    TOKENS_OUT[model_str] = 0
                TOKENS_IN[model_str] += len(encoding.encode(system_prompt + prompt))
                TOKENS_OUT[model_str] += len(encoding.encode(answer))
                if print_cost:
                    print(f"Current experiment cost = ${curr_cost_est()}, ** Approximate values, may not reflect true cost")
            except Exception as e:
                if print_cost: print(f"Cost approximation has an error? {e}")
            return answer
        except Exception as e:
            print(f"Inference Exception: {e}")
            # 如果是未匹配的模型，提供更清晰的错误信息
            if "model_str" in locals() and model_str not in ["gpt-4o-mini", "gpt-4o", "gpt4o", "deepseek-chat", "o1-mini", "o1", "o1-preview", "o3-mini", "claude-3.5-sonnet", "gemini-3-flash-preview", "gemini-1.5-pro", "gemini-2.0-pro", "gpt-5.4-mini"]:
                raise Exception(f"Unsupported model: {model_str}. Please use one of the supported models or check your configuration.")
            time.sleep(timeout)
            continue
    raise Exception("Max retries: timeout")


#print(query_model(model_str="o1-mini", prompt="hi", system_prompt="hey"))
