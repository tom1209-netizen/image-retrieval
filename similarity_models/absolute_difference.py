import numpy as np
from data.data_reader import DataReader


def absolute_difference(query, data):
    axis_batch_size = tuple(range(1, len(data.shape)))
    return np.sum(np.abs(data - query), axis=axis_batch_size)


def get_l1_score(data_reader, query_path, size):
    query = data_reader.read_image_from_path(query_path, size)
    ls_path_score = []
    for folder in data_reader.class_names:
        images_np, images_path = data_reader.folder_to_images(folder, size)
        rates = absolute_difference(query, images_np)
        ls_path_score.extend(list(zip(images_path, rates)))
    return query, ls_path_score


if __name__ == '__main__':
    root_img_path = 'processed/train'
    query_path = 'ambulance/n02701002_773.JPEG'
    size = (224, 224)


    data_reader = DataReader(root=root_img_path)

    query, ls_path_score = get_l1_score(data_reader, query_path, size)

    data_reader.plot_results(query_path=query_path, ls_path_score=ls_path_score, reverse=False)