# Ask user to choose a crop
crop = input("Enter crop type (cassava / maize / rice): ").strip().lower()

if crop not in models:
    print("❌ Invalid crop selected.")
else:
    # Upload image
    uploaded = files.upload()
    image_path = list(uploaded.keys())[0]

    # Set up model details
    model_info = models[crop]

    # Initialize the specific client
    client = InferenceHTTPClient(
        api_url=model_info["api_url"],
        api_key=model_info["api_key"]
    )

    # Make prediction
    result = client.infer(image_path, model_id=model_info["model_id"])
    predictions = result["predictions"]

    print("\n📌 Prediction Results:")
    if predictions:
        # Load the original image here within the successful prediction block
        import cv2
        import matplotlib.pyplot as plt

        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        for pred in predictions:
            label = pred["class"]
            solution = model_info["solutions"].get(label, "No solution available.")
            print(f"- {label.upper()}: {solution}")

            if all(key in pred for key in ["x", "y", "width", "height"]):
                # Get bounding box coordinates
                x1 = int(pred["x"] - pred["width"] / 2)
                y1 = int(pred["y"] - pred["height"] / 2)
                x2 = int(pred["x"] + pred["width"] / 2)
                y2 = int(pred["y"] + pred["height"] / 2)

                # Draw bounding box
                color = (255, 0, 0)  # Red color for bounding box
                thickness = 2
                cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)

                # Put label and confidence
                confidence = pred["confidence"]
                text = f"{label}: {confidence:.2f}"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                text_thickness = 1
                text_size, _ = cv2.getTextSize(text, font, font_scale, text_thickness)
                text_x = x1
                text_y = y1 - 10 if y1 - 10 > 10 else y1 + 10
                cv2.putText(img, text, (text_x, text_y), font, font_scale, color, text_thickness)
            else:
                # Handle predictions without bounding box information (e.g., classification only)
                label = pred["class"]
                confidence = pred["confidence"]
                print(f"Prediction without bounding box: {label} (Confidence: {confidence:.2f})")

        # Display the image with bounding boxes
        plt.figure(figsize=(10, 10))
        plt.imshow(img)
        plt.axis('off')
        plt.title("Image with Predictions")
        plt.show()
    else:
        print("✅ No issue detected. Healthy crop!")
        # Load and display the original image here if no predictions
        import cv2
        import matplotlib.pyplot as plt
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        plt.figure(figsize=(10, 10))
        plt.imshow(img)
        plt.axis('off')
        plt.title("Original Image (No Detections)")
        plt.show()
