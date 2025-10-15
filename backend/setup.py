from setuptools import setup, find_packages

setup(
    name="photopro-ai",
    version="1.0.0",
    description="AI-powered professional photo generation platform",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "gunicorn==21.2.0",
    ],
    python_requires=">=3.11",
)
