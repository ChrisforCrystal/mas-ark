from typing import Annotated
from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")


@mcp.tool
def add(
    a: Annotated[int, "First number to add"], b: Annotated[int, "Second number to add"]
) -> int:
    """Add two integers and return the sum"""
    return a + b


@mcp.tool
def multiply(
    a: Annotated[float, "First number to multiply"],
    b: Annotated[float, "Second number to multiply"],
) -> float:
    """Multiply two numbers and return the product"""
    return a * b


@mcp.tool
def word_count(text: Annotated[str, "Text to analyze for word count"]) -> dict:
    """Count words, characters, and unique words in the given text"""
    words = text.split()
    return {
        "word_count": len(words),
        "char_count": len(text),
        "unique_words": len(set(word.lower() for word in words)),
    }


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000, path="/")
