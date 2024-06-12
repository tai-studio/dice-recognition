import cv2
import numpy as np
import matplotlib.pyplot as plt

def get_edges(img, blur=5, dilate_erode_kerner_size=2, dilate_iterations=3, erode_iterations=1):
    source = img.copy()
    source = cv2.GaussianBlur(source, (blur, blur), 0)
    source = cv2.cvtColor(source, cv2.COLOR_RGB2GRAY)
    source = cv2.normalize(source, None, 0, 255, cv2.NORM_MINMAX)
    # extract edges
    edges = cv2.Canny(source, 90, 200)

    # dilate edges
    kernel = np.ones((dilate_erode_kerner_size, dilate_erode_kerner_size), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=dilate_iterations)

    # # erosion
    edges = cv2.erode(edges, kernel, iterations=erode_iterations)

    return edges


def get_contours (edges, min_area=1000, max_area=2000, verbose=False):

    # find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # approximate contours by their convex hull
    contours = [cv2.convexHull(c) for c in contours]

   # remove small and large  contours
    contours = [c for c in contours if min_area < cv2.contourArea(c) < max_area]

 


    # check if contour is approximately a circle by 
    # comparing the length of the contour with the circumference of a circle with the same area
    contours = [c for c in contours if cv2.arcLength(c, True) < 1.5 * np.pi * cv2.contourArea(c) ** 0.5]

    if verbose:
        # print minimal and maximal contour area
        if len(contours) > 0:
            print(f"min: {min([cv2.contourArea(c) for c in contours])}, max: {max([cv2.contourArea(c) for c in contours])}")
        else:
            print("no contours found")


    return contours

def get_dice_value(img, blur=5, min_area=1000, max_area=20000, verbose=False):
    edges = get_edges(img, blur)
    contours = get_contours(edges, min_area, max_area, verbose)

    if verbose:
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        for c in contours:
            cv2.drawContours(edges, [c], -1, (255, 0, 0), 2)
        plt.imshow(edges)
    return len(contours)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="get dice value from image")
    parser.add_argument("image", help="path to image")
    parser.add_argument("--min", type=float, default=0.3, help="minimum area of contour in percentage")
    parser.add_argument("--max", type=float, default=0.9, help="maximum area of contour in percentage")
    # parser.add_argument("--verbose", action="store_true", help="show image with contours")
    args = parser.parse_args()


    img = cv2.imread(args.image)
    min_area = args.min/100 * img.shape[0] * img.shape[1]
    max_area = args.max/100 * img.shape[0] * img.shape[1]
    print(get_dice_value(img, min_area=min_area, max_area=max_area))
