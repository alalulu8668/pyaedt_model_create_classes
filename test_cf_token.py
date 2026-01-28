from hypha_rpc import connect_to_server
import asyncio
# Connect to Hypha server
async def main():
    server = await connect_to_server({
        "server_url": "https://learning-intelligent-agents-platform.internal.ericsson.com",
        "additional_headers": {
            'cf-access-token': 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjI3YTNjNGIyMTFhYTNkYTYyNzg4ZGFiNTYxNTM0MzFlYWE2MDFjN2U0YTJhM2I0YmM5ZjQxYTMwZjM2NmZjODQifQ.eyJhdWQiOlsiZWVlNTEzMWRhMzZmYzFmMmQ2NmMyOTZlZGZkNDg5YjNlYjE2YjZjOTYzMTBjNTYxMGQ4MDQ4MmFmZDdmYTFkOCJdLCJlbWFpbCI6Indhbmx1LmxlaUBlcmljc3Nvbi5jb20iLCJleHAiOjE3NjE0OTkxMjEsImlhdCI6MTc2MTQxMjcyMSwibmJmIjoxNzYxNDEyNzIxLCJpc3MiOiJodHRwczovL2VyaWNzc29uLmNsb3VkZmxhcmVhY2Nlc3MuY29tIiwidHlwZSI6ImFwcCIsImlkZW50aXR5X25vbmNlIjoiZ0h3Y1RIZXlmeHFwazFTMSIsInN1YiI6IjY2ZDM2Mjk0LTI4MzMtNGNiNi05YjdhLTFhZDlhNDEzZDg0MCIsImNvdW50cnkiOiJVUyJ9.eOFq8EN6ZPHRJBauWy6V-u5SjwkQMb__EPW5jVdTSTjrw5qgoouWeRCy8O_AhAE49lzxrGl-FuXyobge8g2O09xo9yWmfbujlyoHZNW2upKqPf0uleIeIw2dRiJAyAeQOPbIOhxtTSR8Q7WaUPH-V81u7Y4o3X8oN6UK3xH8QDAMADO8DVRjWZqiKlgyrrSTv4hQGU4TBhey1Nd1n2C50O8oPkgVZFC0bFIDM9nrB4KWZ14A6m7ByifIby1auZzDX4-qB_ekTTCYTxe24hHbJAL40RK1nKZmLvcybeTRkj80iiCB15OImtYVTXBd007uD-zrtKpbuW7qGNd5B0iO4Q'
        }
    })
    # Connect to Artifact Manager service
    artifact_manager_service = await server.get_service("public/brawny-index-83659267:artifact-manager")



# # Connect to S3 Storage Service service
# s3_storage_service_service = server.get_service("public/fossil-glazer-43252372:s3-storage")
# print(s3_storage_service_service)
if __name__ == "__main__":
    asyncio.run(main())