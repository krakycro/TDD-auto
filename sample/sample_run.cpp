#include "hdrs/sample.h"

#include <string>

const std::vector< std::vector< int> >&& Global()
{
    return std::vector< std::vector< int> >();
}

namespace factory
{

const std::string& temp(int** a, int b)
{
    return std::string("a");
}

int Run(int argc, char* argv[])
{
    utils::Log("sample");
    return 0;
}

} // namespace factory
