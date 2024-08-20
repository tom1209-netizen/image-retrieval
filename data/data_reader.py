import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction

MODULE_DIR = os.path.dirname(__file__)
embedding_function = OpenCLIPEmbeddingFunction()


class DataReader:
    def __init__(self, root):
        self.root = os.path.join(MODULE_DIR, root)
        self.class_names = sorted(os.listdir(os.path.join(self.root, 'train')))

    def read_image_from_path(self, path, size):
        if not os.path.isabs(path):
            path = os.path.join(self.root, path)
        im = Image.open(path).convert('RGB').resize(size)
        return np.array(im)

    def get_single_image_embedding(self, image):
        embedding = embedding_function._encode_image(image=image)
        return np.array(embedding)

    def folder_to_images(self, folder, size):
        train_folder_path = os.path.join(self.root, 'train')
        current_folder_path = os.path.join(train_folder_path, folder)
        list_dir = [os.path.join(current_folder_path, name) for name in os.listdir(current_folder_path)]
        images_np = np.zeros(shape=(len(list_dir), *size, 3))
        images_path = []
        for i, path in enumerate(list_dir):
            images_np[i] = self.read_image_from_path(path, size)
            images_path.append(path)
        images_path = np.array(images_path)
        return images_np, images_path

    def plot_results(self, query_path, ls_path_score, reverse=False):
        fig = plt.figure(figsize=(15, 9))
        fig.add_subplot(2, 3, 1)
        plt.imshow(self.read_image_from_path(query_path, size=(448, 448)))
        plt.title(f"Query Image: {os.path.basename(query_path)}", fontsize=16)
        plt.axis("off")
        for i, path in enumerate(sorted(ls_path_score, key=lambda x: x[1], reverse=reverse)[:5], 2):
            fig.add_subplot(2, 3, i)
            plt.imshow(self.read_image_from_path(path[0], size=(448, 448)))
            plt.title(f"Top {i - 1}: {os.path.basename(path[0])}", fontsize=16)
            plt.axis("off")
        plt.show()


if __name__ == '__main__':
    data_reader = DataReader(root='processed')
    print(data_reader.class_names)

    images_np, images_path = data_reader.folder_to_images('basketball', size=(224, 224))
    print(images_np.shape)
    print(images_path)