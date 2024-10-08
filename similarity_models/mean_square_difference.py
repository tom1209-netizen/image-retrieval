import numpy as np
from data.data_reader import DataReader


def mean_square_difference(query, data):
    axis_batch_size = tuple(range(1,len(data.shape)))
    return np.mean((data - query)**2, axis=axis_batch_size)


def get_l2_score(data_reader, query_path, size):
    query = data_reader.read_image_from_path(query_path, size)
    query_embedding = data_reader.get_single_image_embedding(query)
    ls_path_score = []
    for folder in data_reader.class_names:
        images_np, images_path = data_reader.folder_to_images(folder, size)
        embedding_list = []
        for idx_img in range(images_np.shape[0]):
            embedding = data_reader.get_single_image_embedding(images_np[idx_img].astype(np.uint8))
            embedding_list.append(embedding)
        rates = mean_square_difference(query_embedding, np.stack(embedding_list))
        ls_path_score.extend(list(zip(images_path, rates)))

    return query, ls_path_score


if __name__ == '__main__':
    root_img_path = 'processed'
    query_path = 'test/Orange_easy/0_100.jpg'
    size = (224, 224)

    data_reader = DataReader(root=root_img_path)

    query, ls_path_score = get_l2_score(data_reader, query_path, size)

    data_reader.plot_results(query_path=query_path, ls_path_score=ls_path_score, reverse=False)