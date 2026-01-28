import asyncio
from hypha_rpc import connect_to_server

async def start_server(server_url):
    # Connect to the Hypha server
    async with connect_to_server({"server_url": server_url}) as server:
        # Define a simple function
        def hello(name):
            print(f"Hello {name}!")
            return f"Hello {name}!"

        # Register the function as a service
        service = await server.register_service({
            "name": "Hello World Service",
            "id": "hello-world",
            "config": {
                "visibility": "public"  # Anyone can use this service
            },
            "hello": hello  # Make our function available
        })

        print(f"✅ Service registered!")
        print(f"Service ID: {service.id}")
        print(f"Workspace: {server.config.workspace}")

        # Keep the service running
        await server.serve()

if __name__ == "__main__":
    server_url = "https://hypha.aicell.io"
    asyncio.run(start_server(server_url))