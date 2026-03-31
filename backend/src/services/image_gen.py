"""AI 插图生成服务 - Stable Diffusion / DALL-E / 通义万相"""

import base64
import io
import random
from abc import ABC, abstractmethod
from typing import Optional

import httpx


class BaseImageGenService(ABC):
    """AI 插图服务基类"""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        style: str = "anime",  # anime/realistic/ink/watercolor/cel_shading
        size: str = "512x512",  # 512x512/1024x1024
        negative_prompt: Optional[str] = None,
        **kwargs
    ) -> dict:  # {url, b64_json, seed, provider}
        """生成插图
        
        Args:
            prompt: 提示词
            style: 风格
            size: 尺寸
            negative_prompt: 反向提示词
            **kwargs: 其他参数
            
        Returns:
            dict: {url, b64_json, seed, provider}
        """
        ...


class StableDiffusionService(BaseImageGenService):
    """Stable Diffusion（本地或远程）"""

    STYLE_SUFFIXES = {
        "anime": "anime style, high quality, detailed",
        "realistic": "photorealistic, hyperrealistic, 8k, detailed",
        "ink": "ink painting style, chinese ink wash, brush stroke",
        "watercolor": "watercolor painting style, soft colors, artistic",
        "cel_shading": "cel shading, anime art style, clean lines",
    }

    SIZE_MAP = {
        "512x512": (512, 512),
        "1024x1024": (1024, 1024),
    }

    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _build_prompt(self, prompt: str, style: str) -> str:
        """构建完整提示词"""
        suffix = self.STYLE_SUFFIXES.get(style, self.STYLE_SUFFIXES["anime"])
        return f"{prompt}, {suffix}"

    async def generate(
        self,
        prompt: str,
        style: str = "anime",
        size: str = "512x512",
        negative_prompt: Optional[str] = None,
        **kwargs
    ) -> dict:
        """调用 Stable Diffusion API 生成图片"""
        width, height = self.SIZE_MAP.get(size, (512, 512))
        seed = kwargs.get("seed", random.randint(0, 4294967295))

        # 构建请求
        full_prompt = self._build_prompt(prompt, style)
        negative = negative_prompt or "low quality, blurry, distorted, deformed"

        payload = {
            "prompt": full_prompt,
            "negative_prompt": negative,
            "width": width,
            "height": height,
            "seed": seed,
            "steps": kwargs.get("steps", 30),
            "cfg_scale": kwargs.get("cfg_scale", 7.0),
        }

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # 调用 SD WebUI API
                response = await client.post(
                    f"{self.base_url}/sdapi/v1/txt2img",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()

                # 提取图片
                image_base64 = result.get("images", [{}])[0]
                if isinstance(image_base64, dict):
                    image_base64 = image_base64.get("image", "")

                return {
                    "url": "",
                    "b64_json": image_base64,
                    "seed": result.get("seed", seed),
                    "provider": "stable_diffusion"
                }

        except httpx.TimeoutException:
            raise RuntimeError("Stable Diffusion 请求超时，请检查服务是否可用")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Stable Diffusion API 错误: {e.response.status_code}")
        except Exception as e:
            raise RuntimeError(f"Stable Diffusion 生成失败: {str(e)}")


class DallEService(BaseImageGenService):
    """OpenAI DALL-E"""

    STYLE_MAP = {
        "anime": "anime style illustration",
        "realistic": "photorealistic image",
        "ink": "ink drawing style",
        "watercolor": "watercolor painting style",
        "cel_shading": "cel-shaded illustration",
    }

    SIZE_MAP = {
        "512x512": "512x512",
        "1024x1024": "1024x1024",
    }

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def generate(
        self,
        prompt: str,
        style: str = "anime",
        size: str = "512x512",
        **kwargs
    ) -> dict:
        """调用 DALL-E API 生成图片"""
        if not self.api_key:
            raise RuntimeError("DALL-E API 密钥未配置")

        # 构建提示词
        style_desc = self.STYLE_MAP.get(style, "")
        full_prompt = f"{prompt}, {style_desc}" if style_desc else prompt

        payload = {
            "model": kwargs.get("model", "dall-e-3"),
            "prompt": full_prompt,
            "n": 1,
            "size": self.SIZE_MAP.get(size, "1024x1024"),
            "response_format": "b64_json",
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/images/generations",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()

                data = result.get("data", [{}])[0]
                return {
                    "url": data.get("url", ""),
                    "b64_json": data.get("b64_json", ""),
                    "seed": 0,
                    "provider": "dall_e"
                }

        except httpx.TimeoutException:
            raise RuntimeError("DALL-E 请求超时，请检查网络连接")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"DALL-E API 错误: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"DALL-E 生成失败: {str(e)}")


class QwenVLService(BaseImageGenService):
    """通义万相（阿里云）"""

    def __init__(self, api_key: str = "", base_url: str = "https://dashscope.aliyuncs.com"):
        self.api_key = api_key
        self.base_url = base_url

    async def generate(
        self,
        prompt: str,
        style: str = "anime",
        size: str = "512x512",
        **kwargs
    ) -> dict:
        """调用通义万相 API 生成图片"""
        if not self.api_key:
            raise RuntimeError("通义万相 API 密钥未配置")

        # 尺寸映射
        size_map = {
            "512x512": "1024*1024",
            "1024x1024": "1024*1024",
        }

        payload = {
            "model": "wanx2.1",
            "input": {
                "prompt": prompt,
                "style": style,
                "size": size_map.get(size, "1024*1024"),
            }
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/services/aigc/text2image/image-synthesis",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()

                # 提取结果
                output = result.get("output", {})
                return {
                    "url": output.get("url", ""),
                    "b64_json": output.get("b64_json", ""),
                    "seed": 0,
                    "provider": "qwen_vl"
                }

        except httpx.TimeoutException:
            raise RuntimeError("通义万相请求超时")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"通义万相 API 错误: {e.response.status_code}")
        except Exception as e:
            raise RuntimeError(f"通义万相生成失败: {str(e)}")


def get_image_gen_service() -> BaseImageGenService:
    """根据配置获取插图服务"""
    from src.core.config import get_settings

    settings = get_settings()
    provider = settings.image_gen_provider  # stable_diffusion / dall_e / qwen_vl

    if provider == "stable_diffusion":
        return StableDiffusionService(
            base_url=settings.image_gen_base_url,
            api_key=settings.image_gen_api_key
        )
    elif provider == "dall_e":
        return DallEService(api_key=settings.image_gen_api_key)
    elif provider == "qwen_vl":
        return QwenVLService(api_key=settings.image_gen_api_key)
    else:
        raise ValueError(f"不支持的图片生成服务: {provider}")
