from typing import Dict, Literal

import pyppeteer
import pyppeteer.errors
from loguru import logger
from pyppeteer.element_handle import ElementHandle
from pyppeteer.page import Page


class ScreenSaver:
    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        do_clip: bool = False,
        clip: Dict[Literal["x", "y", "width", "height"], int] = None,
        type: Literal["png", "jpeg"] = "jpeg",
        quality: int = 100,
    ) -> None:
        self.width = width
        self.height = height
        self.do_clip = do_clip
        self.clip = clip
        self.type = type
        self.quality = quality
        if self.clip is None:
            self.clip = {
                "x": 0,
                "y": 0,
                "width": self.width,
                "height": self.height - 50,
            }
        self.options = {
            "clip": self.clip if self.do_clip else None,
            "type": self.type,
            "quality": self.quality,
        }

    async def preprocess(self, page: Page) -> ElementHandle | None:
        await page.waitForSelector(".PostHeaderSubtitle__link", timeout=15000)
        await page.click(".PostHeaderSubtitle__link")
        await page.waitForSelector(".wk_wall_post_placeholder")
        await page.waitForSelector("#wk_content")
        return await page.querySelector("#wk_content")

    async def screenshot(
        self,
        url: str,
        **options,
    ) -> bytes | None:
        browser = await pyppeteer.launch()
        try:
            page = await browser.newPage()
            await page.goto(url)

            title = await page.title()
            if title.startswith("Ошибка") or title.startswith("Запись удалена"):
                return None

            await page.setViewport(dict(width=self.width, height=self.height))
            if options:  # merge self.options and function options
                self.options = self.options | options
            element = None
            if options.get("wallpost", False):
                element = await self.preprocess(page)
            if element is not None:
                sizes = await element.boundingBox()
                sizes["width"] = (
                    sizes.get("width")
                    if sizes.get("width", 0) <= self.width
                    else self.width
                )
                sizes["height"] = (
                    sizes.get("height")
                    if sizes.get("height", 0) <= self.height
                    else self.height
                )
                self.options["clip"] = sizes
            result = await page.screenshot(self.options)
        except pyppeteer.errors.TimeoutError:
            logger.error("Screenshot timeout error occurred: ", exc_info=True)
        except Exception as error:
            logger.error(
                f"Screenshot unexpected error occurred: {error}",
                exc_info=True,
            )
        else:
            return result
        finally:
            await browser.close()
