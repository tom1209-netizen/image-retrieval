import numpy as np
from data.data_reader import DataReader


def cosine_similarity(query, data):
    axis_batch_size = tuple(range(1, len(data.shape)))

    query_norm = np.sqrt(np.sum(query**2))
    data_norm = np.sqrt(np.sum(data**2, axis=axis_batch_size))

    return np.sum(data * query, axis=axis_batch_size) / (query_norm*data_norm + np.finfo(float).eps)


def get_cosine_similarity_score(data_reader, query_path, size):
    query = data_reader.read_image_from_path(query_path, size)
    query_embedding = data_reader.get_single_image_embedding(query)
    ls_path_score = []

    for folder in data_reader.class_names:
        images_np, images_path = data_reader.folder_to_images(folder, size)


        embeddings = [
            data_reader.get_single_image_embedding(images_np[idx_img].astype(np.uint8))
            for idx_img in range(images_np.shape[0])
        ]

        embeddings = np.stack(embeddings)
        rates = cosine_similarity(query_embedding, embeddings)
        ls_path_score.extend(list(zip(images_path, rates)))

    return query, ls_path_score


if __name__ == '__main__':
    root_img_path = 'processed'
    query_path = 'test/Orange_easy/0_100.jpg'
    size = (224, 224)

    data_reader = DataReader(root=root_img_path)

    query, ls_path_score = get_cosine_similarity_score(data_reader, query_path, size)

    data_reader.plot_results(query_path=query_path, ls_path_score=ls_path_score, reverse=True)