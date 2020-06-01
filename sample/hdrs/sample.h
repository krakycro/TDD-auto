#ifndef SAMPLE_H
#define SAMPLE_H

#include "hdrs/utils/log.h"

#include <iostream>
#include <vector>

const std::vector< std::vector< int> >&& Global();

namespace factory
{

const std::string& temp(int** a, int b);

int Run(int  argc, char*  argv[ ]  );

} // namespace factory

#endif // SAMPLE_H