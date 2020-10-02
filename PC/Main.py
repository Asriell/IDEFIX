from PixMap import PixMap
import cv2
import random as rd


def main():

    img = cv2.imread('test3.bmp', cv2.IMREAD_COLOR)
    #img = cv2.imread('test.bmp', cv2.IMREAD_COLOR)
    # img = cv2.GaussianBlur(img, (5, 5), cv2.BORDER_DEFAULT)
    rot = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    img = cv2.fastNlMeansDenoisingColored(img, None, 5, 5, 7, 21)
    rot = cv2.fastNlMeansDenoisingColored(rot, None, 5, 5, 7, 21)
    # ret, img = cv2.threshold(img, 180, 255, cv2.THRESH_TOZERO)
    rows, cols, encoding = img.shape
    arr = [[[img[y, x][0], img[y, x][1], img[y, x][2]] for x in range(cols)] for y in range(rows)]
    arr2 = [[[rot[y, x][0], rot[y, x][1], rot[y, x][2]] for x in range(cols)] for y in range(rows)]

    cv2.imshow("Input", img)
    px = PixMap()
    px2 = PixMap()
    # PARAMETERS ------------------------
    do_reg_growing = False
    do_reg_merging = False
    do_edge_segmentation = False
    do_signal_segmentation = True
    resize = True
    px.set_tolerance(35)
    # -----------------------------------

    px.feed(arr)
    px2.feed(arr2)

    if do_signal_segmentation:
        px.signal_segmentation()
        for i in range(rows):
            for j in range(cols - 1):
                if px.pm[i * px.width + j].reg_id != px.pm[i * px.width + j + 1].reg_id:
                    img[i, j] = [0, 0, 0]
                else:
                    img[i, j] = [255, 255, 255]

        px2.signal_segmentation()
        for i in range(cols):
            for j in range(rows - 1):
                if px2.pm[i * px2.width + j].reg_id != px2.pm[i * px2.width + j + 1].reg_id:
                    rot[i, j] = [0, 0, 0]
                else:
                    rot[i, j] = [255, 255, 255]
        rot = cv2.rotate(rot, cv2.ROTATE_90_COUNTERCLOCKWISE)
        for i in range(rows):
            for j in range(cols - 1):
                if img[i, j][0] == 0 or rot[i, j][0] == 0:
                    img[i, j] = [0, 0, 0]
        px3 = PixMap()
        px3.feed(img)
        old_img = img.copy()
        px3.signal_segmentation_lining()
        
        for i in range(cols):
            for j in range(rows - 1):
                if px3.pm[i * px3.width + j].potential:
                    img[i, j] = [255, 0, 0]
                elif px3.pm[i * px3.width + j].is_edge:
                    img[i, j] = [0, 0, 0]
                else:
                    img[i, j] = [255, 255, 255]

    if do_reg_growing:
        px.reg_growing_v2()

    if do_reg_merging:
        px.reg_merging()

    if do_edge_segmentation:
        px.fill_with_regions()
        px.edge_segmentation_after_reg_growing()

    if do_reg_growing and not do_edge_segmentation:
        colors = []
        for reg in px.regions:
            colors.append(reg.get_average())
        for i in range(rows):
            for j in range(cols):
                if px.regions[px.pm[i * px.width + j].reg_id].size > 1 or i == 0:
                    img[i, j][0] = colors[px.regions[px.pm[i * px.width + j].reg_id].id][0]
                    img[i, j][1] = colors[px.regions[px.pm[i * px.width + j].reg_id].id][1]
                    img[i, j][2] = colors[px.regions[px.pm[i * px.width + j].reg_id].id][2]

    if do_edge_segmentation:
        for i in range(rows):
            for j in range(cols):
                img[i, j][0] = px.pm[i * px.width + j].r()
                img[i, j][1] = px.pm[i * px.width + j].g()
                img[i, j][2] = px.pm[i * px.width + j].b()

    # img = cv2.fastNlMeansDenoisingColored(img, None, 30, 30, 7, 21)
    # resize image

    scale_percent = 200  # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    # cv2.namedWindow('Input')
    if not do_signal_segmentation:
        old_img = img
    if resize:
        cv2.imshow("Out", resized)
    else:
        cv2.imshow("Out", img)
    cv2.imshow("old", old_img)
    cv2.waitKey(0)

main()
