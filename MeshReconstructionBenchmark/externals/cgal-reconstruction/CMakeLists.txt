cmake_minimum_required(VERSION 3.10)
project(PointCloudReconstruction)

find_package(CGAL REQUIRED CONFIG)
if(CGAL_FOUND)
    set(CGAL_DO_NOT_WARN_ABOUT_CMAKE_BUILD_TYPE TRUE)
    add_definitions( -DCGAL_MINOR_VERSION=${CGAL_MINOR_VERSION} )
    message(STATUS "Found CGAL ${CGAL_VERSION}")
    message(STATUS "  Includes : ${CGAL_INCLUDE_DIRS}")
    message(STATUS "  Libraries : ${CGAL_LIBRARY}")
else()
    message(STATUS "Disabling CGAL support")
endif()
find_package(Eigen3 REQUIRED)
include_directories(${EIGEN3_INCLUDE_DIR})

#add_executable(AdvancingFront AdvancingFront.cpp)
#target_link_libraries(AdvancingFront CGAL::CGAL)
#
#add_executable(ScaleSpace ScaleSpace.cpp)
#target_link_libraries(ScaleSpace CGAL::CGAL)

add_executable(Reconstruct Reconstruct.cpp)
target_link_libraries(Reconstruct CGAL::CGAL)