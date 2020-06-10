import time

import cv2
import mmcv
import numpy as np

from mmmovie import FaceDetector, FaceExtractor

if __name__ == '__main__':
    # demo of face detection
    st = time.time()
    cfg = './model/mtcnn.json'
    weight = './model/mtcnn.pth'
    detector = FaceDetector(cfg, weight)
    print('build model done: {:.2f}s'.format(time.time() - st))

    img_path = './tests/data/titanic.jpg'
    img = mmcv.imread(img_path)
    faces, landmarks = detector.detect(img, show=True)

    num_faces = faces.shape[0]
    print('{} faces detected!'.format(num_faces))
    print('bboxes & confidence:')
    print(faces)
    print('landmarks:')
    print(landmarks)

    # demo of face recognition
    weight_path = './model/irv1_vggface2.pth'
    extractor = FaceExtractor(weight_path, gpu=0)

    img_path = './tests/data/jack.jpg'
    img = mmcv.imread(img_path)
    faces, _ = detector.detect(img)
    face_imgs = detector.crop_face(img, faces)
    assert len(face_imgs) == 1
    feat_jack = extractor.extract(face_imgs[0])
    feat_jack /= np.linalg.norm(feat_jack)

    img_path = './tests/data/rose.jpg'
    img = mmcv.imread(img_path)
    faces, _ = detector.detect(img)
    face_imgs = detector.crop_face(img, faces)
    assert len(face_imgs) == 1
    feat_rose = extractor.extract(face_imgs[0])
    feat_rose /= np.linalg.norm(feat_rose)

    img_path = './tests/data/titanic.jpg'
    img = mmcv.imread(img_path)
    faces, landmarks = detector.detect(img)
    face_imgs = detector.crop_face(img, faces)
    assert len(face_imgs) == 2
    predicts = []
    for i in range(2):
        feat = extractor.extract(face_imgs[i])
        prob_jack = feat[np.newaxis, ...].dot(feat_jack)[0]
        prob_rose = feat[np.newaxis, ...].dot(feat_rose)[0]
        print('face {}: {:.2f} vs. {:.2f}'.format(i, prob_jack, prob_rose))
        if prob_jack > prob_rose:
            predicts.append('jack|{:.2f}'.format(prob_jack))
        else:
            predicts.append('rose|{:.2f}'.format(prob_rose))

    # draw and show
    for i in range(2):
        img = cv2.rectangle(img, (int(faces[i, 0]), int(faces[i, 1])),
                            (int(faces[i, 2]), int(faces[i, 3])), (0, 255, 0),
                            2)
        img = cv2.putText(img, predicts[i],
                          (int(faces[i, 0]), int(faces[i, 1])),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        for j in range(5):
            img = cv2.circle(
                img, (int(landmarks[i, j, 0]), int(landmarks[i, j, 1])), 2,
                (0, 255, 0), 2)
    cv2.imshow('face', img)
    cv2.waitKey()
