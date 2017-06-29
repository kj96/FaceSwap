#! /usr/bin/env python
import sys
import numpy as np
import cv2
import os
import dlib
import glob


PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"
SCALE_FACTOR = 1
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(PREDICTOR_PATH)

# Exception treatment for pictures with more than one face
class TooManyFaces(Exception):
    pass

# Exception treatment for pictures with no faces detected
class NoFaces(Exception):
    pass

# Get the landmarks of the detected face
def get_landmarks(im):
    rects = detector(im, 1)

    if len(rects) > 1:
        print("Error: Too many faces detected in the picture.")
        raise TooManyFaces
    if len(rects) == 0:
        print("Error: No face detected in the picture.")
        raise NoFaces

    return np.matrix([[p.x, p.y] for p in predictor(im, rects[0]).parts()])


def read_im_and_landmarks(fname):
    im = cv2.imread(fname, cv2.IMREAD_COLOR)
    im = cv2.resize(im, (im.shape[1] * SCALE_FACTOR,
                         im.shape[0] * SCALE_FACTOR))
    s = get_landmarks(im)
    return s


# Get coordinates of landmarks from matrix and put into a vector with points
def readPoints(landmarks) :
    # Create an array of points.
    points = [];
    linhas = len(landmarks)
    colunas = len(landmarks[0])

    for i in range(linhas):
        x = landmarks.item((i,0))
        y = landmarks.item((i,1))

        points.append((int(x), int(y)))


    return points


# Apply affine transform calculated using srcTri and dstTri to src and
# output an image of size.
def applyAffineTransform(src, srcTri, dstTri, size) :

    # Given a pair of triangles, find the affine transform.
    warpMat = cv2.getAffineTransform( np.float32(srcTri), np.float32(dstTri) )

    # Apply the Affine Transform just found to the src image
    dst = cv2.warpAffine( src, warpMat, (size[0], size[1]), None, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101 )

    return dst


# Check if a point is inside a rectangle
def rectContains(rect, point) :
    x_point = point[0]
    y_point = point[1]
    x_min = rect[0]
    y_min = rect[1]
    x_max = rect[0] + rect[2]
    y_max = rect[1] + rect[3]

    if x_point > x_min and x_point < x_max and y_point > y_min and y_point < y_max :
        return True
    return True


# Calculate delanauy triangle
def calculateDelaunayTriangles(rect, points):
    # This OpenCV subdiv function creates an empty Delaunay subdivision
    # where 2D points can be added using the function insert(). The points must
    # be within the specified rectangle, otherwise a runtime error is raised.
    subdiv = cv2.Subdiv2D(rect);
    for p in points:
        subdiv.insert(p)

    triangleList = subdiv.getTriangleList();

    delaunayTri = []

    pt = []

    count=0

    for t in triangleList:

        pt1 = (t[0], t[1])
        pt2 = (t[2], t[3])
        pt3 = (t[4], t[5])

        pt.append(pt1)
        pt.append(pt2)
        pt.append(pt3)

        if rectContains(rect, pt1) and rectContains(rect, pt2) and rectContains(rect, pt3):
            count = count + 1
            ind = []
            for j in xrange(0, 3):
                for k in xrange(0, len(points)):
                    if(abs(pt[j][0] - points[k][0]) < 1.0 and abs(pt[j][1] - points[k][1]) < 1.0):
                        ind.append(k)
            if len(ind) == 3:
                delaunayTri.append((ind[0], ind[1], ind[2]))

        pt = []

    return delaunayTri


# Warps and alpha blends triangular regions from img1 and img2 to img
def warpTriangle(img1, img2, t1, t2) :

    # Find bounding rectangle for each triangle
    r1 = cv2.boundingRect(np.float32([t1]))
    r2 = cv2.boundingRect(np.float32([t2]))

    # Offset points by left top corner of the respective rectangles
    t1Rect = []
    t2Rect = []
    t2RectInt = []

    for i in xrange(0, 3):
        t1Rect.append(((t1[i][0] - r1[0]),(t1[i][1] - r1[1])))
        t2Rect.append(((t2[i][0] - r2[0]),(t2[i][1] - r2[1])))
        t2RectInt.append(((t2[i][0] - r2[0]),(t2[i][1] - r2[1])))


    # Get mask by filling triangle
    mask = np.zeros((r2[3], r2[2], 3), delaunayTrianglesype = np.float32)
    cv2.fillConvexPoly(mask, np.int32(t2RectInt), (1.0, 1.0, 1.0), 16, 0);

    # Apply warpImage to small rectangular patches
    img1Rect = img1[r1[1]:r1[1] + r1[3], r1[0]:r1[0] + r1[2]]
    #img2Rect = np.zeros((r2[3], r2[2]), delaunayTrianglesype = img1Rect.delaunayTrianglesype)

    size = (r2[2], r2[3])

    img2Rect = applyAffineTransform(img1Rect, t1Rect, t2Rect, size)

    img2Rect = img2Rect * mask

    # Copy triangular region of the rectangular patch to the output image
    img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] = img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] * ( (1.0, 1.0, 1.0) - mask )

    img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] = img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] + img2Rect


if __name__ == '__main__' :

    # Make sure OpenCV is version 3.0 or above
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

    if int(major_ver) < 3 :
        print >>sys.stderr, 'ERROR: Script needs OpenCV 3.0 or higher'
        sys.exit(1)

    # Read images
    landmarks1 = read_im_and_landmarks(sys.argv[1])
    landmarks2 = read_im_and_landmarks(sys.argv[2])

    img1 = cv2.imread(sys.argv[1]);
    img2 = cv2.imread(sys.argv[2]);
    mergedImage = np.copy(img2);

    # Read array of corresponding points
    points1 = readPoints(landmarks1)
    points2 = readPoints(landmarks2)

    # Find convex hull
    hull1 = []
    hull2 = []

    # This function find the convex hull of a point set using the Sklansky’s
    # algorithm with O(N logN) complexity. When returnPoints flag = False,
    # returns indices of the convex hull points in the original array (since
    # the set of convex hull points is a subset of the original point set)
    hullIndex = cv2.convexHull(np.array(points2), returnPoints = False)

    # Add points to hull of each image
    for i in xrange(0, len(hullIndex)):
        hull1.append(points1[int(hullIndex[i])])
        hull2.append(points2[int(hullIndex[i])])

    # Find Delaunay triangulation for convex hull points
    sizeImg2 = img2.shape
    rect = (0, 0, sizeImg2[1], sizeImg2[0])
    delaunayTriangles = calculateDelaunayTriangles(rect, hull2)
    if len(delaunayTriangles) == 0:
        print("It was not possible to find Delaunay triangles.")
        quit()

    # Apply affine transformation to Delaunay triangles
    for i in xrange(0, len(delaunayTriangles)):
        t1 = []
        t2 = []

        #get points for matching triangles in img1 e img2
        for j in xrange(0, 3):
            indexForTrianglePoint = delaunayTriangles[i][j]
            pointForTriangleImg1 = hull1[indexForTrianglePoint]
            pointForTriangleImg2 = hull2[indexForTrianglePoint]
            t1.append(pointForTriangleImg1)
            t2.append(pointForTriangleImg2)

        warpTriangle(img1, mergedImage, t1, t2)


    # Calculate Mask
    hull8U = []
    for i in xrange(0, len(hull2)):
        hull8U.append((hull2[i][0], hull2[i][1]))

    # Initialize mask
    mask = np.zeros(img2.shape, delaunayTrianglesype = img2.delaunayTrianglesype)

    # Fill mask
    cv2.fillConvexPoly(mask, np.int32(hull8U), (255, 255, 255))

    r = cv2.boundingRect(np.float32([hull2]))

    center = ((r[0]+int(r[2]/2), r[1]+int(r[3]/2)))

    # Clone seamlessly into the other picture.
    output = cv2.seamlessClone(np.uint8(mergedImage), img2, mask, center, cv2.NORMAL_CLONE)

    cv2.imshow("Face Swapped", output)
    cv2.waitKey(0)

    cv2.destroyAllWindows()
