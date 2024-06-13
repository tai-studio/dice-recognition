import cv2
import numpy as np
import matplotlib.pyplot as plt

def prepare_image(img, blur=5, normalise=False, verbose=False):
    source = cv2.GaussianBlur(img, (blur, blur), 0)
    source = cv2.cvtColor(source, cv2.COLOR_RGB2GRAY)
    if normalise:
        source = cv2.normalize(source, None, 0, 255, cv2.NORM_MINMAX)

    if verbose:
        plt.imshow(source, cmap="gray")
        plt.title("preprocessed")
        plt.axis("off")
        plt.show()

    return source

def get_edges(img, canny_low=90, canny_high=200, dilate_erode_kernel_size=2, dilate_iterations=3, erode_iterations=1, verbose=False):

    # extract edges
    edges = cv2.Canny(img, canny_low, canny_high)

    # dilate edges
    kernel = np.ones((dilate_erode_kernel_size, dilate_erode_kernel_size), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=dilate_iterations)

    # # erosion
    edges = cv2.erode(edges, kernel, iterations=erode_iterations)

    if verbose:
        plt.imshow(edges, cmap="gray")
        plt.title("edges")
        plt.axis("off")
        plt.show()

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
            print(f"min: {min([cv2.contourArea(c) for c in contours])},\nmax: {max([cv2.contourArea(c) for c in contours])}")
            print(f"number of contours: {len(contours)}")
        else:
            print("no contours found")
        # draw contours on edges
        img = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        cv2.drawContours(img, contours, -1, (0, 255, 0), 3)
        # add text with number of contours
        cv2.putText(img, f"{len(contours)}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 2)
        plt.imshow(img)
        plt.axis("off")
        plt.title("contours")
        plt.show()

    return contours



def get_dice_value(contours, verbose=False):
    return len(contours)



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="get dice value from image")
    parser.add_argument("image", help="path to image")
    parser.add_argument("--min", type=float, default=0.3, help="minimum area of contour in percentage")
    parser.add_argument("--max", type=float, default=0.9, help="maximum area of contour in percentage")
    parser.add_argument("--kernelSize", type=int, default=2, help="kernel size for dilate and erode")
    parser.add_argument("--dilateIterations", type=int, default=3, help="number of dilate iterations")
    parser.add_argument("--erodeIterations", type=int, default=1, help="number of erode iterations")
    parser.add_argument("--verbose", action="store_true", help="show image with contours")
    parser.add_argument("--normalise", action="store_true", help="normalise image")
    args = parser.parse_args()

    img = cv2.imread(args.image)
    min_area = args.min/100 * img.shape[0] * img.shape[1]
    max_area = args.max/100 * img.shape[0] * img.shape[1]

    img = prepare_image(img, normalise=args.normalise, verbose=args.verbose)
    edges = get_edges(img, dilate_erode_kernel_size=args.kernelSize, dilate_iterations=args.dilateIterations, erode_iterations=args.erodeIterations, verbose=args.verbose)
    contours = get_contours(edges, min_area=min_area, max_area=max_area, verbose=args.verbose)
    value = get_dice_value(contours, verbose=args.verbose)
    print(value)
