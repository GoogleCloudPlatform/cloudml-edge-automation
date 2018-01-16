# from setuptools import setup

# if __name__ == '__main__':
#     setup(name='trainer', packages=['trainer'])


from setuptools import find_packages
from setuptools import setup

REQUIRED_PACKAGES = [
  'google-cloud-storage',
]

if __name__ == '__main__':
    setup(
        name='trainer',
        version='0.1',
        author = 'Google',
        author_email = 'cloudml-feedback@google.com',
        install_requires=REQUIRED_PACKAGES,
        packages=find_packages(),
        include_package_data=True,
        description='Google Cloud Machine Learning flowers example',
        requires=[]
    )
