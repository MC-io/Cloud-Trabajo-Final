from google.cloud import pubsub_v1
import os
# Set your project ID and topic name
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "god-eyes-444201-7a0a8e69bd01.json"

project_id = "god-eyes-444201"
topic_id = "frames"

# Create a Publisher client
publisher = pubsub_v1.PublisherClient()

# Build the topic path
topic_path = publisher.topic_path(project_id, topic_id)

def publish_message(message: str):
    # Data must be a bytestring
    data = message.encode("utf-8")
    
    # Publish the message
    future = publisher.publish(topic_path, data)
    print(f"Published message ID: {future.result()}")

if __name__ == "__main__":
    # Example usage

    publish_message("Hello, Pub/Sub!")