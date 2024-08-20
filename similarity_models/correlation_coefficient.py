import numpy as np
from data.data_reader import DataReader


def correlation_coefficient(query, data):
    axis_batch_size = tuple(range(1,len(data.shape)))
    query_mean = query - np.mean(query)
    data_mean = data - np.mean(data, axis=axis_batch_size, keepdims=True)
    query_norm = np.sqrt(np.sum(query_mean**2))
    data_norm = np.sqrt(np.sum(data_mean**2, axis=axis_batch_size))

    return np.sum(data_mean * query_mean, axis=axis_batch_size) / (query_norm*data_norm + np.finfo(float).eps)


def get_correlation_coefficient_score(data_reader, query_path, size):
    query = data_reader.read_image_from_path(query_path, size)
    query_embedding = data_reader.get_single_image_embedding(query)
    ls_path_score = []
    for folder in data_reader.class_names:
        images_np, images_path = data_reader.folder_to_images(folder, size)
        embedding_list = []
        for idx_img in range(images_np.shape[0]):
            embedding = data_reader.get_single_image_embedding(images_np[idx_img].astype(np.uint8))
            embedding_list.append(embedding)
        rates = correlation_coefficient(query_embedding, np.stack(embedding_list))
        ls_path_score.extend(list(zip(images_path, rates)))
    return query, ls_path_score


if __name__ == '__main__':
    root_img_path = 'processed'
    query_path = 'test/Orange_easy/0_100.jpg'
    size = (224, 224)

    data_reader = DataReader(root=root_img_path)

    query, ls_path_score = get_correlation_coefficient_score(data_reader, query_path, size)

    data_reader.plot_results(query_path=query_path, ls_path_score=ls_path_score, reverse=True)
