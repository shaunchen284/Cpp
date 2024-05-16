cmake_minimum_required(VERSION 3.28)
project(Cpp)

set(CMAKE_CXX_STANDARD 14)

include_directories(.)

add_executable(Cpp
        test.cpp
        test.h)
