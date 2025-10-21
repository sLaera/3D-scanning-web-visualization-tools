#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel;
typedef Kernel::Point_3 Point;

bool read_ply(const std::string& filename, std::vector<Point>& points) {
    std::ifstream in(filename, std::ios::binary);
    if (!in) {
        std::cerr << "Cannot load PLY: " << filename << "\n";
        return false;
    }

    std::string line;
    bool header_ended = false;
    while (std::getline(in, line)) {
        if (line == "end_header") {
            header_ended = true;
            break;
        }
    }

    if (!header_ended) {
        std::cerr << "PLY format not valid: missing 'end_header'.\n";
        return false;
    }

    double x, y, z;
    while (in >> x >> y >> z) {
        points.emplace_back(x, y, z);
    }

    in.close();
    return true;
}
