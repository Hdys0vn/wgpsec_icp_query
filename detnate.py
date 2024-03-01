from ultralytics import YOLO
from siamese import Siamese
import cv2
from PIL import Image
import numpy as np


class detnate:
    def __init__(self) -> None:
        self.comp_model = Siamese()
        self.det_model = YOLO(model='model_data/best.onnx', task='detect')
        self.small_selice_four_index = [
                [
                    {'x':163,'y':9},
                    {'x':193,'y':41}
                ],[
                    {'x':198,'y':9},
                    {'x':225,'y':41}
                ],[
                    {'x':230,'y':9},
                    {'x':259,'y':41}
                ],[
                    {'x':263,'y':9},
                    {'x':294,'y':41}
                ]
            ]
        
    def check_target_ibig(self,ibig):
        '''
        参考文章：https://mp.weixin.qq.com/s/1Dw7ylfRmBjV_khOF4nuGQ

        检测big中的文字,返回索引、坐标、map
        '''

        # show=True，显示检测结果
        results = self.det_model.predict(source=ibig, show=False, imgsz=320)
        for result in results:
            cls_xy = list()
            cls_dict = result.names
            cls_all = result.boxes.cls.tolist()
            xyxy_all = result.boxes.xyxy.tolist()
            for i in range(len(cls_all)):
                label_name = cls_dict[int(cls_all[i])]
                box_xyxy = xyxy_all[i]
                box_mid_xy = [(box_xyxy[0] + box_xyxy[2]) / 2, (box_xyxy[1] + box_xyxy[3]) / 2]
                x_min, y_min, x_max, y_max = map(int, box_xyxy)
                cropped_image = ibig[y_min:y_max, x_min:x_max]
                cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
                cropped_image = Image.fromarray(cropped_image)
                cls_xy.append({
                    "label_id": i, "label_name": label_name,
                    "box_mid_xy": box_mid_xy, "xyxy": box_xyxy,
                    "img":cropped_image
                })
            return cls_xy

    def check_target(self,ibig,isma):
        '''
        检测大图和小图并返回结果
        '''
        ibig_result = self.check_target_ibig(ibig)
        det_comp_result = []
        for i in self.small_selice_four_index:
            undet_sim = isma[i[0]['y']:i[1]['y'],i[0]['x']:i[1]['x']]
            undet_sim = cv2.cvtColor(undet_sim, cv2.COLOR_BGR2RGB)
            undet_sim = Image.fromarray(undet_sim)

            # 存储相似度
            sim_big_comp = []
            for bigimg in ibig_result:
                undet_big = bigimg['img']
                det = self.comp_model.detect_image(undet_sim,undet_big)
                sim_big_comp.append([det.item(),bigimg['box_mid_xy']])

            # 取最相似的坐标
            max_value = float('-inf')
            max_coords = None
            for item in sim_big_comp:
                if item[0] > max_value:
                    max_value = item[0]
                    max_coords = item[1]
            det_comp_result.append(max_coords)

            # 想查看绘制结果的话就取消这些注释,93-95也要取消
            # 在ibig上绘制识别结果,顺手伪描边
            # text = str(self.small_selice_four_index.index(i))
            # max_coords[0], max_coords[1] =  max_coords[0] - 11,max_coords[1] + 12 
            # cv2.putText(ibig, text, tuple(int(x) for x in max_coords), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
            # cv2.putText(ibig, text, tuple(int(x) for x in max_coords), cv2.FONT_HERSHEY_SIMPLEX, 1, (238, 154, 0), 1)
            # new_image = np.vstack((ibig, isma))

        # 显示绘制结果
        # cv2.imshow('Image with Text', new_image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        data = [{'x':int(i[0]),'y':int(i[1])} for i in det_comp_result]

        del ibig
        del isma
        del undet_sim
        del undet_big

        return data



if __name__ == "__main__":
    a = detnate()
    bigimg = cv2.imread('test_img/ibig/716.jpg')
    smaimg = cv2.imread('test_img/isma/716.jpg')
    a.check_target(bigimg,smaimg)