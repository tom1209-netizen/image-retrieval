import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from tqdm import tqdm
import chromadb

MODULE_DIR = os.path.dirname(__file__)


class DataReader:
    def __init__(self, root):
        self.root = os.path.join(MODULE_DIR, root)
        self.class_names = sorted(os.listdir(os.path.join(self.root, 'train')))
        self.embedding_function = OpenCLIPEmbeddingFunction()
        self.chroma_client = chromadb.Client()
        self.hnsw_space = "hnsw:space"

    def read_image_from_path(self, path, size):
        if not os.path.isabs(path):
            path = os.path.join(self.root, path)
        try:
            im = Image.open(path).convert('RGB').resize(size)
            return np.array(im)
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None

    def get_files_path(self, path):
        files_path = []
        for label in self.class_names:
            label_path = os.path.join(path, label)
            try:
                filenames = os.listdir(label_path)
                for filename in filenames:
                    filepath = os.path.join(label_path, filename)
                    files_path.append(filepath)
            except FileNotFoundError:
                print(f"Directory not found: {label_path}")
        return files_path

    def get_single_image_embedding(self, image):
        try:
            image_array = np.array(image)
            embedding = self.embedding_function._encode_image(image=image_array)
            return embedding
        except Exception as e:
            print(f"Error creating embedding: {e}")
            return None

    def folder_to_images(self, folder, size):
        current_folder_path = os.path.join(self.root, 'train', folder)
        list_dir = [os.path.join(current_folder_path, name) for name in os.listdir(current_folder_path)]
        images_np = np.zeros(shape=(len(list_dir), *size, 3))
        images_path = []
        for i, path in enumerate(list_dir):
            image = self.read_image_from_path(path, size)
            if image is not None:
                images_np[i] = image
                images_path.append(path)
        return images_np, np.array(images_path)

    def add_embedding(self, collection, files_path):
        ids = []
        embeddings = []
        for id_filepath, filepath in tqdm(enumerate(files_path)):
            ids.append(f'id_{id_filepath}')
            image = Image.open(filepath)
            embedding = self.get_single_image_embedding(image=image)
            if embedding is not None:
                embeddings.append(embedding)
        collection.add(embeddings=embeddings, ids=ids)

    def create_collection(self, name, space):
        return self.chroma_client.get_or_create_collection(name=name, metadata={self.hnsw_space: space})

    def search(self, image_path, collection, n_results=5):
        query_image = Image.open(image_path)
        query_embedding = self.get_single_image_embedding(query_image)
        if query_embedding is not None:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            return results
        else:
            print(f"Error in searching for {image_path}. No results found.")
            return None

    def plot_results(self, query_path, files_path, results, reverse=False):
        if results is None:
            print("No results to plot.")
            return

        fig = plt.figure(figsize=(15, 9))
        fig.add_subplot(2, 3, 1)
        plt.imshow(self.read_image_from_path(query_path, size=(448, 448)))
        plt.title(f"Query Image: {os.path.basename(query_path)}", fontsize=16)
        plt.axis("off")

        for i, path in enumerate(sorted(results['ids'][0], key=lambda x: x[1], reverse=reverse)[:5], 2):
            image_path = files_path[int(path.split('_')[-1])]
            plt.subplot(2, 3, i)
            plt.imshow(self.read_image_from_path(image_path, size=(448, 448)))
            plt.title(f"Top {i - 1}: {os.path.basename(image_path)}")
            plt.axis("off")
        plt.show()


if __name__ == '__main__':
    data_reader = DataReader(root='processed')

    # Training set
    train_path = os.path.join(data_reader.root, 'train')
    train_files_path = data_reader.get_files_path(path=train_path)

    # Add embeddings to L2 collection
    l2_collection = data_reader.create_collection(name="l2_collection", space="l2")
    data_reader.add_embedding(collection=l2_collection, files_path=train_files_path)

    # Add embeddings to Cosine collection
    cosine_collection = data_reader.create_collection(name="cosine_collection", space="cosine")
    data_reader.add_embedding(collection=cosine_collection, files_path=train_files_path)

    # Testing set
    test_path = os.path.join(data_reader.root, 'test')
    test_files_path = data_reader.get_files_path(path=test_path)
    test_image_path = test_files_path[1]

    # Search in L2 collection
    l2_results = data_reader.search(image_path=test_image_path, collection=l2_collection, n_results=5)
    data_reader.plot_results(query_path=test_image_path, files_path=train_files_path, results=l2_results)