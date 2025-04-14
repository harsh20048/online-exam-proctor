import os
import urllib.request

def download_file(url, filename):
    print(f"Downloading {filename}...")
    urllib.request.urlretrieve(url, filename)
    print(f"Downloaded {filename}")

def main():
    # Create models directory if it doesn't exist
    if not os.path.exists('models'):
        os.makedirs('models')
        
    # Download face detection model files
    model_urls = {
        'res10_300x300_ssd_iter_140000.caffemodel': 'https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20180205_float/res10_300x300_ssd_iter_140000.caffemodel',
        'deploy.prototxt': 'https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt'
    }
    
    for filename, url in model_urls.items():
        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            download_file(url, filename)
        else:
            print(f"{filename} already exists")

if __name__ == "__main__":
    main() 